import os, re, sqlite3, csv, smtplib, math, time, io, json
import datetime as dt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

import requests, stripe
from flask import (
    Flask, render_template, request, redirect, url_for, flash, abort,
    Response, session, send_file, jsonify
)
from flask_compress import Compress

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ---------------- App ----------------
app = Flask(__name__)
Compress(app)
app.secret_key = os.environ.get("SECRET_KEY", "dev_key")

DB_PATH     = os.environ.get("DB_PATH", "bookings.db")
EMAIL_USER  = os.environ.get("EMAIL_USER", "")
EMAIL_PASS  = os.environ.get("EMAIL_PASS", "")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", EMAIL_USER or "")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT   = int(os.environ.get("SMTP_PORT", "587"))

ADMIN_USER  = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS  = os.environ.get("ADMIN_PASS", "admin123")

GA_ID       = os.environ.get("GA_ID", "")  # اختياري

# Stripe (اختياري)
STRIPE_SECRET_KEY      = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
stripe.api_key = STRIPE_SECRET_KEY
CURRENCY = "sar"

# Moyasar (محلي)
MOYASAR_PUBLISHABLE_KEY = os.environ.get("MOYASAR_PUBLISHABLE_KEY", "")
MOYASAR_SECRET_KEY      = os.environ.get("MOYASAR_SECRET_KEY", "")

# إشعارات تيليجرام
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")

# بيانات الفاتورة/الشركة
COMPANY_NAME    = os.environ.get("COMPANY_NAME", "وجهة السعودية")
TAX_NUMBER      = os.environ.get("TAX_NUMBER", "")
COMPANY_EMAIL   = os.environ.get("COMPANY_EMAIL", ADMIN_EMAIL)
COMPANY_PHONE   = os.environ.get("COMPANY_PHONE", "")
COMPANY_ADDRESS = os.environ.get("COMPANY_ADDRESS", "المملكة العربية السعودية")
INVOICE_LOGO    = os.environ.get("INVOICE_LOGO", "")  # مثال: static/images/logo.png
INVOICE_FONT    = os.environ.get("INVOICE_FONT", "")  # مثال: static/fonts/Cairo-Regular.ttf


# ---------------- CSRF & Rate limit ----------------
def ensure_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = os.urandom(16).hex()
    return session["csrf_token"]

def check_csrf():
    tok = request.form.get("_csrf")
    return tok and tok == session.get("csrf_token")

RATE_LIMIT = {}
RATE_WINDOW = 60  # ثانية
RATE_MAX = 5
def allow_post(ip):
    now = time.time()
    lst = RATE_LIMIT.get(ip, [])
    lst = [t for t in lst if now - t < RATE_WINDOW]
    if len(lst) >= RATE_MAX:
        RATE_LIMIT[ip] = lst
        return False
    lst.append(now); RATE_LIMIT[ip] = lst
    return True


# ---------------- DB ----------------
def _add_column_if_missing(cur, table, col, typ):
    cur.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cur.fetchall()]
    if col not in cols:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typ}")

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            trip TEXT NOT NULL,
            date TEXT NOT NULL,
            people INTEGER NOT NULL,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    _add_column_if_missing(cur, "bookings", "user_id", "INTEGER")
    _add_column_if_missing(cur, "bookings", "payment_status", "TEXT DEFAULT 'unpaid'")
    _add_column_if_missing(cur, "bookings", "stripe_session_id", "TEXT")
    _add_column_if_missing(cur, "bookings", "coupon_code", "TEXT")
    _add_column_if_missing(cur, "bookings", "discount_halala", "INTEGER DEFAULT 0")
    _add_column_if_missing(cur, "bookings", "invoice_no", "TEXT")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS payment_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER,
            gateway TEXT,
            payment_id TEXT,
            status TEXT,
            amount INTEGER,
            currency TEXT,
            raw_json TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS promo_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            kind TEXT,
            value INTEGER,
            active INTEGER DEFAULT 1,
            expires_at TEXT,
            usage_limit INTEGER,
            used_count INTEGER DEFAULT 0,
            min_amount INTEGER DEFAULT 0
        )
    """)
    con.commit(); con.close()

def db(): return sqlite3.connect(DB_PATH)

def save_booking(name, email, phone, trip, date, people, notes, user_id=None):
    con = db(); cur = con.cursor()
    cur.execute("""INSERT INTO bookings (name,email,phone,trip,date,people,notes,user_id,payment_status)
                   VALUES (?,?,?,?,?,?,?,?, 'unpaid')""",
                (name,email,phone,trip,date,int(people),notes,user_id))
    con.commit(); bid = cur.lastrowid; con.close(); return bid

def update_booking(bid, **fields):
    if not fields: return
    con = db(); cur = con.cursor()
    sets = ", ".join([f"{k}=?" for k in fields.keys()])
    cur.execute(f"UPDATE bookings SET {sets} WHERE id=?", list(fields.values()) + [int(bid)])
    con.commit(); con.close()

def delete_booking(bid):
    con = db(); cur = con.cursor()
    cur.execute("DELETE FROM bookings WHERE id=?", (int(bid),))
    con.commit(); con.close()

def get_booking(bid):
    con = db(); cur = con.cursor()
    cur.execute("""
        SELECT id,name,email,phone,trip,date,people,notes,created_at,user_id,
               payment_status,stripe_session_id,coupon_code,discount_halala,invoice_no
        FROM bookings WHERE id=?
    """, (int(bid),))
    r = cur.fetchone(); con.close(); return r

def query_bookings(q=None, start=None, end=None, page=1, per_page=10, order="id DESC"):
    con = db(); cur = con.cursor()
    params, where = [], []
    if q:
        where.append("(name LIKE ? OR email LIKE ? OR phone LIKE ? OR trip LIKE ? OR date LIKE ?)")
        kw = f"%{q}%"; params += [kw,kw,kw,kw,kw]
    if start: where.append("date >= ?"); params.append(start)
    if end:   where.append("date <= ?"); params.append(end)
    base_sql = "FROM bookings"
    if where: base_sql += " WHERE " + " AND ".join(where)
    cur.execute(f"SELECT COUNT(*) {base_sql}", params); total = cur.fetchone()[0]
    offset = (page - 1) * per_page
    cur.execute(f"SELECT id,name,email,phone,trip,date,people,notes,created_at,user_id,payment_status,stripe_session_id {base_sql} ORDER BY {order} LIMIT ? OFFSET ?",
                params + [per_page, offset])
    rows = cur.fetchall(); con.close(); return rows, total

def log_payment(booking_id, gateway, payment_id, status, amount, currency, raw_json):
    con = db(); cur = con.cursor()
    cur.execute("""INSERT INTO payment_logs (booking_id,gateway,payment_id,status,amount,currency,raw_json)
                   VALUES (?,?,?,?,?,?,?)""",
                (booking_id, gateway, payment_id, status, int(amount) if amount is not None else None, currency, raw_json))
    con.commit(); con.close()

def query_payments(q=None, page=1, per_page=15, order="id DESC"):
    con = db(); cur = con.cursor()
    params, where = [], []
    if q:
        where.append("(gateway LIKE ? OR payment_id LIKE ? OR status LIKE ? OR currency LIKE ? OR CAST(booking_id AS TEXT) LIKE ?)")
        kw = f"%{q}%"; params += [kw,kw,kw,kw,kw]
    base_sql = "FROM payment_logs"
    if where: base_sql += " WHERE " + " AND ".join(where)
    cur.execute(f"SELECT COUNT(*) {base_sql}", params); total = cur.fetchone()[0]
    offset = (page - 1) * per_page
    cur.execute(f"SELECT id,booking_id,gateway,payment_id,status,amount,currency,created_at {base_sql} ORDER BY {order} LIMIT ? OFFSET ?",
                params + [per_page, offset])
    rows = cur.fetchall(); con.close(); return rows, total


# ---------------- Utilities ----------------
def is_valid_email(addr: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", (addr or "").strip()))

def send_email(subject: str, html_body: str, to_email: str, text_fallback: str = None):
    if not (EMAIL_USER and EMAIL_PASS and is_valid_email(to_email)):
        print("Email config invalid or recipient invalid; skipping send."); return False
    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_USER; msg["To"] = to_email; msg["Subject"] = subject
    msg.attach(MIMEText(text_fallback or "رسالة من وجهة السعودية", "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT); server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS); server.sendmail(EMAIL_USER, to_email, msg.as_string()); server.quit()
        return True
    except Exception as e:
        print("Email send error:", e); return False

def send_email_with_attachment(subject: str, html_body: str, to_email: str, filename: str, data_bytes: bytes, mimetype="application/pdf"):
    if not (EMAIL_USER and EMAIL_PASS and is_valid_email(to_email)):
        print("Email config invalid or recipient invalid; skipping send (attachment)."); return False
    msg = MIMEMultipart("mixed")
    msg["From"] = EMAIL_USER; msg["To"] = to_email; msg["Subject"] = subject
    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText("انظر المرفق.", "plain", "utf-8"))
    alt.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(alt)
    part = MIMEBase("application", "octet-stream")
    part.set_payload(data_bytes); encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
    msg.attach(part)
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT); server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS); server.sendmail(EMAIL_USER, to_email, msg.as_string()); server.quit()
        return True
    except Exception as e:
        print("Email with attachment error:", e); return False

def email_template_admin(name, email, phone, trip, date, people, notes):
    return f"""
    <div style="font-family:Tahoma,Arial,sans-serif;line-height:1.8;color:#222">
      <h2 style="margin:0 0 10px;color:#234d20">📩 حجز جديد</h2>
      <table style="width:100%;max-width:520px;border-collapse:collapse">
        <tr><td>👤 الاسم:</td><td><strong>{name}</strong></td></tr>
        <tr><td>📧 البريد:</td><td>{email}</td></tr>
        <tr><td>📱 الجوال:</td><td>{phone}</td></tr>
        <tr><td>🏝️ الرحلة:</td><td>{trip}</td></tr>
        <tr><td>📅 التاريخ:</td><td>{date}</td></tr>
        <tr><td>👥 الأشخاص:</td><td>{people}</td></tr>
        <tr><td>📝 الملاحظات:</td><td>{notes or '-'}</td></tr>
      </table>
    </div>
    """

def email_template_user(name, trip, date, people):
    return f"""
    <div style="font-family:Tahoma,Arial,sans-serif;line-height:1.9;color:#222">
      <h2 style="margin:0 0 6px;color:#234d20">مرحباً {name} 👋</h2>
      <p>شكرًا لحجزك لدى <strong>وجهة السعودية</strong>. تفاصيل طلبك:</p>
      <ul>
        <li>🏝️ الرحلة: <strong>{trip}</strong></li>
        <li>📅 التاريخ: <strong>{date}</strong></li>
        <li>👥 عدد الأشخاص: <strong>{people}</strong></li>
      </ul>
      <p>سنتواصل معك قريبًا لتأكيد التفاصيل.</p>
    </div>
    """

def send_booking_emails(name, email, phone, trip, date, people, notes):
    admin_html = email_template_admin(name, email, phone, trip, date, people, notes)
    admin_txt  = f"حجز جديد من {name}\nرحلة: {trip}\nتاريخ: {date}\nأشخاص: {people}\nجوال: {phone}\nملاحظات: {notes or '-'}"
    send_email(subject=f"📩 حجز جديد من {name}", html_body=admin_html, to_email=ADMIN_EMAIL, text_fallback=admin_txt)
    if is_valid_email(email):
        user_html = email_template_user(name, trip, date, people)
        user_txt  = f"مرحباً {name}\nتم استلام حجزك لِـ {trip} بتاريخ {date} لعدد {people}."
        send_email(subject="✅ تأكيد حجزك لدى وجهة السعودية", html_body=user_html, to_email=email, text_fallback=user_txt)

# Telegram notify
def notify_telegram(message: str):
    if not (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID): return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
        return True
    except Exception as e:
        print("Telegram notify error:", e); return False

def notify_admin_all_channels(title: str, lines: list[str]):
    msg = f"🔔 {title}\n" + "\n".join(lines)
    return notify_telegram(msg)


# ---------------- i18n ----------------
TR = {
    "ar": {"home":"الرئيسية","booking":"الحجز","contact":"تواصل","gallery":"المعرض","login":"دخول","register":"حساب جديد","account":"حجوزاتي","logout":"خروج"},
    "en": {"home":"Home","booking":"Booking","contact":"Contact","gallery":"Gallery","login":"Login","register":"Sign up","account":"My Bookings","logout":"Logout"},
}
def get_lang(): return "ar"
def t(k): return TR["ar"].get(k,k)


# ---------------- Trips data ----------------
TRIPS = {
    "riyadh": {
        "slug":"riyadh","title":"رحلة الرياض","image":"images/riyadh_1.JPG",
        "summary":"تعرف على العاصمة ومعالمها الحديثة والتراثية.","duration":"يوم كامل","price":"399 ريال","amount":399,
        "highlights":["زيارة بوليفارد سيتي","جولة في قصر المصمك","تجربة المأكولات الشعبية"],
        "itinerary":["الانطلاق صباحًا","زيارة قصر المصمك","الغداء","جولة مسائية في البوليفارد"],
        "includes":["مرشد سياحي","مواصلات","وجبة غداء"],"lat":24.7136,"lng":46.6753,
    },
    "jeddah": {
        "slug":"jeddah","title":"رحلة جدة","image":"images/jeddah_1.JPG",
        "summary":"جولة على كورنيش جدة والمعالم التاريخية.","duration":"يوم كامل","price":"349 ريال","amount":349,
        "highlights":["التنزه في الكورنيش","زيارة جدة التاريخية","جلسة غروب"],
        "itinerary":["الانطلاق صباحًا","زيارة البلد","الغداء على الواجهة البحرية","جلسة غروب"],
        "includes":["مرشد سياحي","مواصلات"],"lat":21.4858,"lng":39.1925,
    },
}


# ---------------- Amounts / Coupons ----------------
def find_promo(code: str):
    if not code: return None
    con = db(); cur = con.cursor()
    cur.execute("""SELECT id,code,kind,value,active,expires_at,usage_limit,used_count,min_amount
                   FROM promo_codes WHERE LOWER(code)=LOWER(?)""", (code.strip(),))
    r = cur.fetchone(); con.close()
    if not r: return None
    return {"id":r[0],"code":r[1],"kind":r[2],"value":r[3],"active":bool(r[4]),
            "expires_at":r[5],"usage_limit":r[6],"used_count":r[7],"min_amount":r[8] or 0}

def promo_valid(p, amount_halala: int):
    if not p or not p["active"]: return (False,"الكوبون غير فعال.")
    if p["expires_at"]:
        try:
            if dt.date.today() > dt.date.fromisoformat(p["expires_at"]):
                return (False,"انتهت صلاحية الكوبون.")
        except: pass
    if p["usage_limit"] is not None and p["used_count"] is not None:
        if int(p["used_count"]) >= int(p["usage_limit"]):
            return (False,"تم استنفاد استخدامات هذا الكوبون.")
    if amount_halala < int(p["min_amount"] or 0):
        return (False,"لا ينطبق الكوبون على هذا المبلغ.")
    return (True,"")

def apply_promo_amount(amount_halala: int, code: str):
    p = find_promo(code)
    if not p: return (amount_halala, 0, "الكوبون غير موجود.", False)
    ok, msg = promo_valid(p, amount_halala)
    if not ok: return (amount_halala, 0, msg, False)
    if p["kind"] == "percent": disc = int(round(amount_halala * (p["value"] / 100.0)))
    else: disc = int(p["value"])
    disc = max(0, min(disc, amount_halala))
    return (amount_halala - disc, disc, "تم تطبيق الخصم.", True)

def promo_increment_usage(code: str):
    if not code: return
    con = db(); cur = con.cursor()
    cur.execute("UPDATE promo_codes SET used_count = COALESCE(used_count,0)+1 WHERE LOWER(code)=LOWER(?)", (code.strip(),))
    con.commit(); con.close()

def booking_amount_halala(b):
    trip_key = None
    for k,v in TRIPS.items():
        if v["title"] == b[4] or v["slug"] == b[4]:
            trip_key = k; break
    base = TRIPS.get(trip_key, {}).get("amount", 300)
    qty  = int(b[6] or 1)
    amount = int(base * qty * 100)
    discount = int(b[13] or 0)
    return max(0, amount - discount)


# ---------------- Invoice helpers ----------------
def generate_invoice_no(bid: int) -> str:
    return f"SD-{dt.date.today():%Y%m}-{int(bid):06d}"

def ensure_invoice_no(bid: int):
    con = db(); cur = con.cursor()
    cur.execute("SELECT invoice_no FROM bookings WHERE id=?", (int(bid),))
    r = cur.fetchone()
    inv = r[0] if r else None
    if not inv:
        inv = generate_invoice_no(bid)
        cur.execute("UPDATE bookings SET invoice_no=? WHERE id=?", (inv, int(bid)))
        con.commit()
    con.close(); return inv

def get_last_paid_payment(booking_id: int):
    con = db(); cur = con.cursor()
    cur.execute("""
        SELECT gateway, payment_id, status, amount, currency, created_at
        FROM payment_logs
        WHERE booking_id=? AND status='paid'
        ORDER BY id DESC LIMIT 1
    """, (int(booking_id),))
    r = cur.fetchone(); con.close()
    if not r: return None
    return {"gateway":r[0],"payment_id":r[1],"status":r[2],"amount":r[3],"currency":r[4] or "SAR","created_at":r[5]}

def build_invoice_pdf_bytes(b, pay):
    # خط عربي اختياري
    try:
        if INVOICE_FONT and os.path.exists(INVOICE_FONT):
            pdfmetrics.registerFont(TTFont("AR", INVOICE_FONT))
            FONT_REG = "AR"; FONT_BOLD = "AR"
        else:
            FONT_REG = "Helvetica"; FONT_BOLD = "Helvetica-Bold"
    except Exception:
        FONT_REG = "Helvetica"; FONT_BOLD = "Helvetica-Bold"

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    mx = 36; y = h - 36

    # شعار
    try:
        if INVOICE_LOGO and os.path.exists(INVOICE_LOGO):
            c.drawImage(INVOICE_LOGO, mx, y-60, width=120, height=50, preserveAspectRatio=True, mask='auto')
    except Exception: pass

    c.setFont(FONT_BOLD, 18); c.drawString(w-220, y-12, "فاتورة دفع")
    c.setFont(FONT_REG, 10);  c.drawString(w-220, y-30, dt.date.today().isoformat()); y -= 72

    # الشركة
    c.setFont(FONT_BOLD, 12); c.drawString(mx, y, COMPANY_NAME); y -= 16
    c.setFont(FONT_REG, 10)
    if COMPANY_ADDRESS: c.drawString(mx, y, COMPANY_ADDRESS); y -= 14
    if COMPANY_PHONE:   c.drawString(mx, y, f"الهاتف: {COMPANY_PHONE}"); y -= 14
    if COMPANY_EMAIL:   c.drawString(mx, y, f"البريد: {COMPANY_EMAIL}"); y -= 14
    if TAX_NUMBER:      c.drawString(mx, y, f"الرقم الضريبي: {TAX_NUMBER}"); y -= 18
    y -= 6

    c.setLineWidth(0.6); c.line(mx, y, w-mx, y); y -= 18

    # بيانات الحجز
    c.setFont(FONT_BOLD, 12); c.drawString(mx, y, "بيانات الحجز"); y -= 16
    c.setFont(FONT_REG, 10)
    inv_no = b[14] or "-"
    fields = [("رقم الفاتورة", inv_no), ("رقم الحجز", str(b[0])), ("الاسم", b[1]), ("البريد", b[2]),
              ("الجوال", b[3]), ("الرحلة", b[4]), ("تاريخ الرحلة", b[5]), ("عدد الأشخاص", str(b[6])), ("حالة الدفع", b[10] or "unpaid")]
    for k, v in fields:
        c.drawString(mx, y, f"{k}: {v}"); y -= 14

    y -= 6; c.setLineWidth(0.6); c.line(mx, y, w-mx, y); y -= 18

    c.setFont(FONT_BOLD, 12); c.drawString(mx, y, "التفاصيل المالية"); y -= 16
    c.setFont(FONT_REG, 10)
    if pay:
        amount_sar = (pay["amount"] or 0) / 100.0
        table = [("البوابة", pay["gateway"]), ("رقم العملية", pay["payment_id"]),
                 ("المبلغ", f"{amount_sar:.2f} {pay['currency']}"), ("تاريخ العملية", pay["created_at"])]
    else:
        table = [("الحالة", "لا توجد عملية مدفوعة مسجلة بعد")]

    rows_h = 18 * len(table) + 6
    c.setFillGray(0.95); c.rect(mx, y-rows_h+6, w-2*mx, rows_h, fill=1, stroke=0); c.setFillGray(0)
    ry = y
    for k, v in table:
        c.setFont(FONT_BOLD, 10); c.drawString(mx+8, ry, k)
        c.setFont(FONT_REG, 10); c.drawString(mx+180, ry, str(v)); ry -= 18
    y = ry - 10

    # QR: Booking-<id>
    try:
        qr_text = f"Booking-{b[0]}"
        qrw = qr.QrCodeWidget(qr_text)
        size = 100
        d = Drawing(size, size); d.add(qrw)
        renderPDF.draw(d, c, w - mx - size, 60)
        c.setFont(FONT_REG, 8); c.drawRightString(w - mx, 56, qr_text)
    except Exception as e:
        print("QR build error:", e)

    c.setFont(FONT_REG, 9)
    c.drawString(mx, 50, "الشروط: يحق الإلغاء قبل 48 ساعة لاسترداد كامل، وقد تُطبق رسوم بعد ذلك.")
    c.showPage(); c.save(); buffer.seek(0)
    return buffer.getvalue()

def send_payment_notifications(bid: int):
    b = get_booking(bid)
    if not b: return
    pay = get_last_paid_payment(bid)
    if not pay: return
    ensure_invoice_no(bid)
    pdf_bytes = build_invoice_pdf_bytes(get_booking(bid), pay)
    filename = f"invoice_{b[0]}.pdf"
    # للمستخدم
    if is_valid_email(b[2]):
        send_email_with_attachment(
            subject=f"فاتورة دفع حجز #{b[0]}",
            html_body=f"<p>تم استلام دفعتك بنجاح. مرفق الفاتورة.</p>",
            to_email=b[2], filename=filename, data_bytes=pdf_bytes
        )
    # للإدارة
    send_email_with_attachment(
        subject=f"دفعة ناجحة – حجز #{b[0]}",
        html_body=f"<p>تم استلام دفعة ناجحة لحجز #{b[0]} ({b[4]} - {b[1]}).</p>",
        to_email=ADMIN_EMAIL, filename=filename, data_bytes=pdf_bytes
    )


# ---------------- Context ----------------
@app.context_processor
def inject_globals():
    return {
        "csrf_token": ensure_csrf_token(),
        "GA_ID": GA_ID,
        "t": t, "lang": get_lang(),
        "STRIPE_PUBLISHABLE_KEY": STRIPE_PUBLISHABLE_KEY,
        "MOYASAR_PUBLISHABLE_KEY": MOYASAR_PUBLISHABLE_KEY,
    }


# ---------------- Routes ----------------
@app.route("/")
def home(): return render_template("home.html", trips=TRIPS)

@app.route("/trip/<slug>")
def trip_detail(slug):
    trip = TRIPS.get(slug)
    if not trip: abort(404)
    return render_template("trip_detail.html", trip=trip)

@app.route("/booking", methods=["GET","POST"])
def booking():
    if request.method == "POST":
        if not allow_post(request.remote_addr or "0.0.0.0"):
            flash("محاولات كثيرة. حاول لاحقاً.", "error"); return redirect(url_for("booking"))
        if not check_csrf():
            flash("جلسة غير صالحة.", "error"); return redirect(url_for("booking"))
        if request.form.get("website"):  # honeypot
            flash("تم رفض الطلب.", "error"); return redirect(url_for("booking"))

        name   = request.form.get("name","").strip()
        email  = request.form.get("email","").strip()
        phone  = request.form.get("phone","").strip()
        trip   = request.form.get("trip","").strip()
        date   = request.form.get("date","").strip()
        people = request.form.get("people","1").strip()
        notes  = request.form.get("notes","").strip()
        if not all([name,email,phone,trip,date,people]):
            flash("فضلاً أكمل جميع الحقول.", "error"); return redirect(url_for("booking"))

        bid = save_booking(name, email, phone, trip, date, people, notes)
        send_booking_emails(name, email, phone, trip, date, people, notes)
        # إشعار تيليجرام
        notify_admin_all_channels("حجز جديد", [f"#{bid} | {name}", f"رحلة: {trip}", f"تاريخ: {date}", f"أشخاص: {people}"])
        return redirect(url_for("success", id=bid))
    return render_template("booking.html", trips=TRIPS)

@app.route("/success")
def success():
    bid = request.args.get("id")
    b = get_booking(bid) if bid else None
    return render_template("success.html", b=b)

# Stripe
@app.route("/pay/<int:bid>")
def pay_now(bid):
    if not STRIPE_SECRET_KEY:
        flash("الدفع عبر Stripe غير مُفعّل.", "error"); return redirect(url_for("success", id=bid))
    b = get_booking(bid);  abort(404) if not b else None
    amount_after = booking_amount_halala(b) // 100
    session_obj = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{
            "price_data": {"currency": CURRENCY, "product_data": {"name": b[4]}, "unit_amount": int(amount_after*100)},
            "quantity": 1,
        }],
        customer_email=b[2],
        success_url=url_for("payment_success", bid=bid, _external=True),
        cancel_url=url_for("payment_cancel", bid=bid, _external=True),
        allow_promotion_codes=False,
    )
    update_booking(bid, stripe_session_id=session_obj.id)
    return redirect(session_obj.url, code=303)

@app.route("/payment/success")
def payment_success():
    bid = request.args.get("bid")
    if bid:
        update_booking(bid, payment_status="paid")
        ensure_invoice_no(int(bid))
        try:
            send_payment_notifications(int(bid))
            notify_admin_all_channels("دفعة ناجحة (Stripe)", [f"حجز #{bid}", "تم التحديث إلى Paid"])
            promo_increment_usage(get_booking(int(bid))[12])
        except Exception as e:
            print("notify on stripe success error:", e)
    flash("تم الدفع بنجاح. شكرًا لك!", "success")
    return redirect(url_for("success", id=bid))

@app.route("/payment/cancel")
def payment_cancel():
    bid = request.args.get("bid")
    flash("تم إلغاء عملية الدفع.", "error")
    return redirect(url_for("success", id=bid))

# Moyasar
@app.route("/pay/moyasar/<int:bid>")
def pay_moyasar(bid):
    if not MOYASAR_PUBLISHABLE_KEY:
        flash("الدفع المحلي غير مُفعّل. أضف مفاتيح Moyasar.", "error")
        return redirect(url_for("success", id=bid))
    b = get_booking(bid); abort(404) if not b else None

    # احسب المبلغ الأصلي
    trip_key = None
    for k,v in TRIPS.items():
        if v["title"] == b[4] or v["slug"] == b[4]:
            trip_key = k; break
    base = TRIPS.get(trip_key, {}).get("amount", 300)
    qty  = int(b[6] or 1)
    original_amount = int(base * qty * 100)

    code = (request.args.get("code") or b[12] or "").strip()
    if code:
        new_amount, disc, msg, ok = apply_promo_amount(original_amount, code)
        if ok:
            update_booking(bid, coupon_code=code, discount_halala=disc)
            flash(f"{msg} (خصم: {disc/100:.2f} ريال)", "success")
        else:
            flash(msg, "error")

    b = get_booking(bid)
    amount = booking_amount_halala(b)
    return render_template("pay_moyasar.html", b=b, amount_halala=amount,
                           original_amount_halala=original_amount,
                           discount_halala=int(b[13] or 0))

@app.route("/payment/moyasar/callback", methods=["GET","POST"])
def moyasar_callback():
    payment_id = request.values.get("id") or request.values.get("payment_id")
    booking_id = request.values.get("booking_id") or request.values.get("metadata[booking_id]") or request.values.get("metadata.booking_id")
    if not payment_id or not booking_id:
        flash("تعذر التحقق من عملية الدفع.", "error")
        return redirect(url_for("success", id=booking_id or ""))

    try:
        resp = requests.get(f"https://api.moyasar.com/v1/payments/{payment_id}",
                            auth=(MOYASAR_SECRET_KEY, ""), timeout=15)
        data = resp.json()
        status = (data or {}).get("status")
        amount = (data or {}).get("amount")
        currency = (data or {}).get("currency") or "SAR"
        log_payment(booking_id, "moyasar", payment_id, status, amount, currency, json.dumps(data, ensure_ascii=False))
        if status == "paid":
            update_booking(booking_id, payment_status="paid")
            ensure_invoice_no(int(booking_id))
            try:
                send_payment_notifications(int(booking_id))
                notify_admin_all_channels("دفعة ناجحة (Moyasar)", [f"حجز #{booking_id}", "تم التحديث إلى Paid"])
                promo_increment_usage(get_booking(int(booking_id))[12])
            except Exception as e:
                print("notify on moyasar callback error:", e)
            flash("تم الدفع بنجاح عبر Moyasar. شكرًا لك!", "success")
        else:
            flash("عملية الدفع لم تُستكمل بنجاح.", "error")
    except Exception as e:
        print("Moyasar verify error:", e)
        flash("حصل خطأ أثناء التحقق من الدفع.", "error")

    return redirect(url_for("success", id=booking_id))

@app.route("/webhooks/moyasar", methods=["POST"])
def moyasar_webhook():
    try:
        payload = request.get_json(silent=True) or {}
        payment_id = payload.get("id") or payload.get("payment_id")
        metadata = payload.get("metadata") or {}
        booking_id = metadata.get("booking_id") or request.args.get("booking_id")
        if not payment_id: return jsonify({"ok": False, "error": "missing id"}), 400

        r = requests.get(f"https://api.moyasar.com/v1/payments/{payment_id}",
                         auth=(MOYASAR_SECRET_KEY, ""), timeout=15)
        data = r.json()
        status = (data or {}).get("status")
        amount = (data or {}).get("amount")
        currency = (data or {}).get("currency") or "SAR"
        if not booking_id:
            booking_id = (data.get("metadata") or {}).get("booking_id")

        log_payment(booking_id, "moyasar", payment_id, status, amount, currency, json.dumps(data, ensure_ascii=False))
        if booking_id and status == "paid":
            update_booking(booking_id, payment_status="paid")
            ensure_invoice_no(int(booking_id))
            try:
                send_payment_notifications(int(booking_id))
                notify_admin_all_channels("دفعة ناجحة (Webhook Moyasar)", [f"حجز #{booking_id}", f"عملية: {payment_id}"])
                promo_increment_usage(get_booking(int(booking_id))[12])
            except Exception as e:
                print("notify on moyasar webhook error:", e)
        return jsonify({"ok": True})
    except Exception as e:
        print("Webhook error:", e)
        return jsonify({"ok": False}), 500


# Invoice & Receipt
@app.route("/invoice/<int:bid>.pdf")
def invoice_pdf(bid):
    b = get_booking(bid)
    if not b: abort(404)
    pay = get_last_paid_payment(bid)
    if not pay: return redirect(url_for("booking_pdf", bid=bid))
    pdf_bytes = build_invoice_pdf_bytes(b, pay)
    return send_file(io.BytesIO(pdf_bytes), as_attachment=True, download_name=f"invoice_{b[0]}.pdf", mimetype="application/pdf")

@app.route("/receipt/<int:bid>.pdf")
def booking_pdf(bid):
    b = get_booking(bid);  abort(404) if not b else None
    buffer = io.BytesIO(); c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica-Bold", 16); c.drawString(40, 800, "إيصال حجز – وجهة السعودية")
    c.setFont("Helvetica", 12)
    y = 770
    for k,v in [("رقم الحجز",b[0]),("الاسم",b[1]),("البريد",b[2]),("الجوال",b[3]),("الرحلة",b[4]),("التاريخ",b[5]),("الأشخاص",b[6]),("الحالة",b[10] or 'unpaid')]:
        c.drawString(40, y, f"{k}: {v}"); y -= 18
    c.showPage(); c.save(); buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"receipt_{b[0]}.pdf", mimetype="application/pdf")


# Contact
@app.route("/contact", methods=["GET","POST"])
def contact():
    if request.method == "POST":
        if not check_csrf(): abort(400)
        name=request.form.get("name","").strip(); email=request.form.get("email","").strip(); msg=request.form.get("message","").strip()
        if not all([name,email,msg]): flash("فضلاً أكمل جميع الحقول.", "error"); return redirect(url_for("contact"))
        con = db(); cur = con.cursor(); cur.execute("INSERT INTO contacts (name,email,message) VALUES (?,?,?)",(name,email,msg)); con.commit(); con.close()
        send_email(subject=f"📬 رسالة تواصل من {name}", html_body=f"<p><b>الاسم:</b> {name}</p><p><b>البريد:</b> {email}</p><p>{msg}</p>", to_email=ADMIN_EMAIL, text_fallback=f"من {name} ({email}):\n{msg}")
        flash("تم إرسال رسالتك، شكرًا لتواصلك.", "success"); return redirect(url_for("contact"))
    return render_template("contact.html")


# Gallery
def list_gallery():
    folder = os.path.join(app.static_folder, "images", "gallery"); items=[]
    if os.path.isdir(folder):
        for f in os.listdir(folder):
            if f.lower().endswith((".jpg",".jpeg",".png",".webp",".gif")):
                items.append("images/gallery/" + f)
    items.sort(); return items

@app.route("/gallery")
def gallery(): return render_template("gallery.html", images=list_gallery())


# Robots/Sitemap
@app.route("/robots.txt")
def robots_txt():
    return Response("User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n", mimetype="text/plain")

@app.route("/sitemap.xml")
def sitemap_xml():
    base = request.url_root.rstrip("/")
    urls = ["/", "/booking", "/contact", "/gallery"] + [f"/trip/{k}" for k in TRIPS.keys()]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    today = dt.date.today().isoformat()
    for u in urls:
        xml += [f"<url><loc>{base}{u}</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq></url>"]
    xml.append("</urlset>")
    return Response("\n".join(xml), mimetype="application/xml")


# Admin (مبسطة)
def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*a, **kw):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login", next=request.path))
        return fn(*a, **kw)
    return wrapper

@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("username")==ADMIN_USER and request.form.get("password")==ADMIN_PASS:
            session["is_admin"]=True; flash("تم تسجيل الدخول", "success")
            return redirect(request.args.get("next") or url_for("admin_dashboard"))
        flash("بيانات الدخول غير صحيحة", "error"); return redirect(url_for("admin_login"))
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear(); flash("تم تسجيل الخروج", "success")
    return redirect(url_for("admin_login"))

@app.route("/admin")
@login_required
def admin_dashboard():
    q   = request.args.get("q","").strip()
    start = request.args.get("start","").strip()
    end   = request.args.get("end","").strip()
    page = max(1, int(request.args.get("page","1") or "1"))
    per_page = 10
    rows, total = query_bookings(q=q, start=start or None, end=end or None, page=page, per_page=per_page)
    pages = max(1, math.ceil(total/per_page))
    return render_template("admin_dashboard.html", bookings=rows, total=total, q=q, start=start, end=end, page=page, pages=pages, per_page=per_page)

@app.route("/admin/bookings.csv")
@login_required
def export_bookings_csv():
    q   = request.args.get("q","").strip()
    start = request.args.get("start","").strip()
    end   = request.args.get("end","").strip()
    rows, _ = query_bookings(q=q, start=start or None, end=end or None, page=1, per_page=10**6)
    def generate():
        output = io.StringIO(); writer = csv.writer(output)
        writer.writerow(["id","name","email","phone","trip","date","people","notes","created_at","user_id","payment_status","stripe_session_id"])
        yield output.getvalue(); output.seek(0); output.truncate(0)
        for r in rows:
            writer.writerow(r); yield output.getvalue(); output.seek(0); output.truncate(0)
    return Response(generate(), mimetype="text/csv",
                    headers={"Content-Disposition":"attachment; filename=bookings.csv"})

@app.route("/admin/booking/<int:bid>/delete", methods=["POST"])
@login_required
def admin_delete(bid):
    if not check_csrf(): abort(400)
    delete_booking(bid); flash("تم حذف الحجز", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/booking/<int:bid>/edit", methods=["GET","POST"])
@login_required
def admin_edit(bid):
    if request.method == "POST":
        if not check_csrf(): abort(400)
        name=request.form.get("name",""); email=request.form.get("email","")
        phone=request.form.get("phone",""); trip=request.form.get("trip","")
        date=request.form.get("date",""); people=request.form.get("people","1")
        notes=request.form.get("notes",""); pay=request.form.get("payment_status","unpaid")
        update_booking(bid, name=name, email=email, phone=phone, trip=trip, date=date, people=int(people), notes=notes, payment_status=pay)
        flash("تم تحديث الحجز", "success"); return redirect(url_for("admin_dashboard"))
    b = get_booking(bid);  abort(404) if not b else None
    return render_template("admin_edit.html", b=b)

@app.route("/admin/payments")
@login_required
def admin_payments():
    q   = request.args.get("q","").strip()
    page = max(1, int(request.args.get("page","1") or "1"))
    per_page = 15
    rows, total = query_payments(q=q, page=page, per_page=per_page)
    pages = max(1, math.ceil(total/per_page))
    return render_template("admin_payments.html", payments=rows, total=total, q=q, page=page, pages=pages, per_page=per_page)

@app.route("/admin/payments.csv")
@login_required
def export_payments_csv():
    q   = request.args.get("q","").strip()
    rows, _ = query_payments(q=q, page=1, per_page=10**6)
    def generate():
        output = io.StringIO(); writer = csv.writer(output)
        writer.writerow(["id","booking_id","gateway","payment_id","status","amount","currency","created_at"])
        yield output.getvalue(); output.seek(0); output.truncate(0)
        for r in rows:
            writer.writerow(r); yield output.getvalue(); output.seek(0); output.truncate(0)
    return Response(generate(), mimetype="text/csv",
                    headers={"Content-Disposition":"attachment; filename=payments.csv"})

@app.route("/admin/reports")
@login_required
def admin_reports():
    con = db(); cur = con.cursor()
    cur.execute("""SELECT substr(created_at,1,7) AS ym, COUNT(*), COALESCE(SUM(amount),0)
                   FROM payment_logs WHERE status='paid' GROUP BY ym ORDER BY ym DESC""")
    monthly = cur.fetchall()
    cur.execute("""SELECT b.trip, COUNT(pl.id), COALESCE(SUM(pl.amount),0)
                   FROM bookings b LEFT JOIN payment_logs pl ON pl.booking_id=b.id AND pl.status='paid'
                   GROUP BY b.trip ORDER BY 3 DESC""")
    by_trip = cur.fetchall()
    con.close()
    return render_template("admin_reports.html", monthly=monthly, by_trip=by_trip)


# Errors
@app.errorhandler(404)
def not_found(e): return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e): return render_template("500.html"), 500


# Bootstrap
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    init_db()