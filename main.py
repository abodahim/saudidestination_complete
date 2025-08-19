# -*- coding: utf-8 -*-
from flask import send_from_directory
import os
import os, sqlite3, io, smtplib, ssl, secrets
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, send_file, abort
)
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# -----------------------------------------------------------------------------
# إعداد التطبيق
# -----------------------------------------------------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", secrets.token_hex(16))
DB_PATH = os.getenv("DB_PATH", "app.db")

# إعدادات البريد (يفضّل Gmail + كلمة مرور تطبيق)
MAIL_HOST  = os.getenv("MAIL_HOST", "smtp.gmail.com")
MAIL_PORT  = int(os.getenv("MAIL_PORT", "587"))  # 465 SSL أو 587 TLS
MAIL_USER  = os.getenv("MAIL_USER", "")
MAIL_PASS  = os.getenv("MAIL_PASS", "")
MAIL_FROM  = os.getenv("MAIL_FROM", MAIL_USER)
MAIL_ADMIN = os.getenv("MAIL_ADMIN", MAIL_USER)  # نسخة إدارية

# مستخدم لوحة الإدارة
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")

# -----------------------------------------------------------------------------
# قاعدة البيانات
# -----------------------------------------------------------------------------
def get_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    con = get_db(); cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        trip TEXT NOT NULL,
        date TEXT,
        people INTEGER DEFAULT 1,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_id INTEGER,
        payment_status TEXT DEFAULT 'unpaid',
        stripe_session_id TEXT,
        coupon_code TEXT,
        discount_halala INTEGER DEFAULT 0,
        invoice_no TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL,
        gateway TEXT,
        payment_id TEXT,
        status TEXT,
        amount INTEGER,
        currency TEXT DEFAULT 'SAR',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (booking_id) REFERENCES bookings(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
        comment TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    con.commit()

init_db()

# -----------------------------------------------------------------------------
# مساعدات
# -----------------------------------------------------------------------------
def send_email(to_email: str, subject: str, html_body: str, bcc_admin=True):
    """إرسال بريد عبر SMTP؛ يرجع True عند النجاح"""
    if not (MAIL_USER and MAIL_PASS and MAIL_FROM):
        return False
    msg = MIMEMultipart("alternative")
    msg["From"], msg["To"], msg["Subject"] = MAIL_FROM, to_email, subject
    if bcc_admin and MAIL_ADMIN:
        msg["Bcc"] = MAIL_ADMIN
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    try:
        if MAIL_PORT == 465:
            ctx = ssl.create_default_context()
            with smtplib.SMTP_SSL(MAIL_HOST, MAIL_PORT, context=ctx) as s:
                s.login(MAIL_USER, MAIL_PASS)
                s.sendmail(MAIL_FROM, [to_email] + ([MAIL_ADMIN] if bcc_admin else []), msg.as_string())
        else:
            with smtplib.SMTP(MAIL_HOST, MAIL_PORT) as s:
                s.ehlo(); s.starttls(); s.login(MAIL_USER, MAIL_PASS)
                s.sendmail(MAIL_FROM, [to_email] + ([MAIL_ADMIN] if bcc_admin else []), msg.as_string())
        return True
    except Exception as e:
        print("EMAIL_ERROR:", e)
        return False

def format_amount(halala):  # إلى ريال
    try:
        return f"{(halala or 0)/100:.2f}"
    except Exception:
        return "0.00"

def make_invoice_number(bid: int) -> str:
    return f"INV-{datetime.now().strftime('%y%m%d')}-{bid:05d}"

# -----------------------------------------------------------------------------
# مراجعات (BLL)
# -----------------------------------------------------------------------------
def add_review(name: str, rating: int, comment: str):
    name = (name or "").strip()[:80]
    comment = (comment or "").strip()[:1000]
    try: rating = int(rating)
    except: rating = 0
    if not (name and comment and 1 <= rating <= 5): return False
    con = get_db(); cur = con.cursor()
    cur.execute("INSERT INTO reviews (name, rating, comment) VALUES (?,?,?)", (name, rating, comment))
    con.commit(); return True

def fetch_reviews(limit=100):
    con = get_db(); cur = con.cursor()
    cur.execute("""SELECT id,name,rating,comment,created_at
                   FROM reviews ORDER BY created_at DESC LIMIT ?""", (limit,))
    return cur.fetchall()

# -----------------------------------------------------------------------------
# صفحات عامة
# -----------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name  = request.form.get("name","").strip()
        email = request.form.get("email","").strip()
        msg   = request.form.get("message","").strip()
        if not (name and email and msg):
            flash("الرجاء تعبئة جميع الحقول.", "error")
            return redirect(url_for("contact"))
        try:
            html_user = f"<p>مرحباً {name} 👋</p><p>وصلتنا رسالتك وسنعود لك قريباً.</p><p>نص الرسالة:</p><blockquote>{msg}</blockquote>"
            send_email(email, "تم استلام رسالتك – وجهة السعودية", html_user, bcc_admin=False)
            html_admin = f"<p><strong>اسم:</strong> {name}<br><strong>بريد:</strong> {email}</p><p>{msg}</p>"
            if MAIL_ADMIN:
                send_email(MAIL_ADMIN, "📨 رسالة جديدة من صفحة التواصل", html_admin, bcc_admin=False)
            flash("تم إرسال رسالتك بنجاح ✅", "success")
        except Exception as e:
            print("CONTACT_EMAIL_ERR:", e)
            flash("تعذر إرسال الرسالة حالياً.", "error")
        return redirect(url_for("contact"))
    return render_template("contact.html")

@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        name  = request.form.get("name","").strip()
        email = request.form.get("email","").strip()
        phone = request.form.get("phone","").strip()
        trip  = request.form.get("trip","").strip()
        date  = request.form.get("date") or ""
        people= int(request.form.get("people") or 1)
        notes = request.form.get("notes","").strip()

        if not (name and email and phone and trip):
            flash("الرجاء تعبئة الحقول الأساسية", "error")
            return redirect(url_for("booking"))

        con = get_db(); cur = con.cursor()
        cur.execute("""INSERT INTO bookings
            (name,email,phone,trip,date,people,notes)
            VALUES (?,?,?,?,?,?,?)""",
            (name,email,phone,trip,date,people,notes))
        con.commit()
        bid = cur.lastrowid

        # بريد تأكيد
        try:
            body = render_template("email_booking.html",
                                   name=name, trip=trip, bid=bid, date=date, people=people)
            send_email(email, f"تأكيد استلام طلب الحجز #{bid}", body)
        except Exception as e:
            print("EMAIL_BOOKING_ERROR:", e)

        return redirect(url_for("thank_you", bid=bid))
    return render_template("booking.html")

@app.route("/thank-you/<int:bid>")
def thank_you(bid):
    con = get_db(); cur = con.cursor()
    cur.execute("SELECT * FROM bookings WHERE id=?", (bid,))
    b = cur.fetchone()
    if not b: abort(404)
    return render_template("thank_you.html", b=b)

# صفحة الدفع + بوابات محاكية
@app.route("/payment/<int:bid>")
def payment(bid):
    con = get_db(); cur = con.cursor()
    cur.execute("SELECT * FROM bookings WHERE id=?", (bid,))
    b = cur.fetchone()
    if not b: abort(404)
    return render_template("payment.html", b=b)

@app.route("/pay/moyasar/<int:bid>")
def pay_moyasar(bid):  # دفع محلي
    return _mark_paid_and_redirect(bid, "Moyasar")

@app.route("/pay/stripe/<int:bid>")
def pay_now(bid):      # دفع ببطاقة
    return _mark_paid_and_redirect(bid, "Stripe")

def _mark_paid_and_redirect(bid: int, gateway: str):
    con = get_db(); cur = con.cursor()
    cur.execute("SELECT * FROM bookings WHERE id=?", (bid,))
    b = cur.fetchone()
    if not b: abort(404)

    amount_halala = (b[6] or 1) * 200 * 100  # 200 ريال/شخص كمثال
    invoice_no = make_invoice_number(bid)

    cur.execute("""INSERT INTO payments (booking_id, gateway, payment_id, status, amount, currency)
                   VALUES (?,?,?,?,?,?)""",
                (bid, gateway, f"{gateway}-{datetime.now().timestamp():.0f}", "paid", amount_halala, "SAR"))
    cur.execute("UPDATE bookings SET payment_status='paid', invoice_no=? WHERE id=?", (invoice_no, bid))
    con.commit()

    # بريد ما بعد الدفع
    try:
        html = render_template("email_paid.html",
                               name=b[1], bid=bid, invoice_no=invoice_no,
                               amount=format_amount(amount_halala))
        send_email(b[2], f"تم الدفع بنجاح – فاتورتك #{invoice_no}", html)
    except Exception as e:
        print("EMAIL_AFTER_PAYMENT_ERROR:", e)

    flash("تم الدفع بنجاح ✅", "success")
    return redirect(url_for("payment", bid=bid))

# -----------------------------------------------------------------------------
# PDF: إيصال الحجز + الفاتورة
# -----------------------------------------------------------------------------
def _simple_pdf(title, lines):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    y = h - 50
    c.setFont("Helvetica-Bold", 16); c.drawString(50, y, title)
    c.setFont("Helvetica", 11); y -= 30
    for ln in lines:
        c.drawString(50, y, str(ln)); y -= 18
        if y < 60: c.showPage(); y = h - 50; c.setFont("Helvetica", 11)
    c.showPage(); c.save(); buf.seek(0); return buf

@app.route("/receipt/<int:bid>.pdf")
def booking_pdf(bid):
    con = get_db(); cur = con.cursor()
    cur.execute("SELECT * FROM bookings WHERE id=?", (bid,))
    b = cur.fetchone()
    if not b: abort(404)
    lines = [
        f"رقم الحجز: #{b[0]}",
        f"الاسم: {b[1]}",
        f"البريد: {b[2]}",
        f"الجوال: {b[3]}",
        f"الرحلة: {b[4]}",
        f"التاريخ: {b[5]}",
        f"عدد الأشخاص: {b[6]}",
        f"حالة الدفع: {b[10]}",
        f"أُنشئ في: {b[8]}",
    ]
    return send_file(_simple_pdf("إيصال الحجز", lines),
                     mimetype="application/pdf", as_attachment=True,
                     download_name=f"booking-{b[0]}.pdf")

@app.route("/invoice/<int:bid>.pdf")
def invoice_pdf(bid):
    con = get_db(); cur = con.cursor()
    cur.execute("SELECT * FROM bookings WHERE id=?", (bid,))
    b = cur.fetchone()
    if not b: abort(404)
    cur.execute("""SELECT amount,gateway,payment_id,created_at
                   FROM payments WHERE booking_id=? AND status='paid'
                   ORDER BY id DESC LIMIT 1""", (bid,))
    p = cur.fetchone()
    if not p: abort(404)
    lines = [
        f"فاتورة رقم: {b[14] or make_invoice_number(bid)}",
        f"رقم الحجز: #{b[0]}",
        f"الاسم: {b[1]}",
        f"الرحلة: {b[4]}",
        f"التاريخ: {b[5]}",
        f"عدد الأشخاص: {b[6]}",
        f"البوابة: {p[1]}",
        f"رقم العملية: {p[2]}",
        f"الإجمالي (SAR): {format_amount(p[0])}",
        f"تاريخ العملية: {p[3]}",
    ]
    return send_file(_simple_pdf("فاتورة الدفع", lines),
                     mimetype="application/pdf", as_attachment=True,
                     download_name=f"invoice-{b[0]}.pdf")

# -----------------------------------------------------------------------------
# مراجعات
# -----------------------------------------------------------------------------
@app.route("/reviews", methods=["GET", "POST"])
def reviews():
    if request.method == "POST":
        ok = add_review(request.form.get("name"),
                        request.form.get("rating"),
                        request.form.get("comment"))
        flash("تم إضافة تقييمك بنجاح 🌟" if ok else "تعذر إضافة التقييم.", "success" if ok else "error")
        return redirect(url_for("reviews"))
    return render_template("reviews.html", reviews=fetch_reviews(100))

# -----------------------------------------------------------------------------
# لوحة الإدارة
# -----------------------------------------------------------------------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if (request.form.get("username")==ADMIN_USER and
            request.form.get("password")==ADMIN_PASS):
            session["admin"]=True
            return redirect(url_for("admin_dashboard"))
        flash("بيانات الدخول غير صحيحة", "error")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))

def admin_required():
    if not session.get("admin"): abort(403)

@app.route("/admin")
def admin_dashboard():
    admin_required()
    q = (request.args.get("q") or "").strip()
    page = max(int(request.args.get("page", 1)), 1); per = 20; off = (page-1)*per
    con = get_db(); cur = con.cursor()
    if q:
        like = f"%{q}%"
        cur.execute("""SELECT * FROM bookings
                       WHERE name LIKE ? OR email LIKE ? OR phone LIKE ? OR trip LIKE ? OR payment_status LIKE ?
                       ORDER BY created_at DESC LIMIT ? OFFSET ?""",
                    (like, like, like, like, like, per, off))
        total = con.execute("""SELECT count(*) FROM bookings
                               WHERE name LIKE ? OR email LIKE ? OR phone LIKE ? OR trip LIKE ? OR payment_status LIKE ?""",
                             (like, like, like, like, like)).fetchone()[0]
    else:
        cur.execute("""SELECT * FROM bookings
                       ORDER BY created_at DESC LIMIT ? OFFSET ?""", (per, off))
        total = con.execute("SELECT count(*) FROM bookings").fetchone()[0]
    rows = cur.fetchall(); pages = (total + per - 1)//per
    return render_template("admin_dashboard.html", rows=rows, page=page, pages=pages, q=q)

@app.route("/admin/edit/<int:bid>", methods=["GET","POST"])
def admin_edit(bid):
    admin_required()
    con = get_db(); cur = con.cursor()
    cur.execute("SELECT * FROM bookings WHERE id=?", (bid,)); b = cur.fetchone()
    if not b: abort(404)
    if request.method == "POST":
        name  = request.form.get("name","").strip()
        email = request.form.get("email","").strip()
        phone = request.form.get("phone","").strip()
        trip  = request.form.get("trip","").strip()
        date  = request.form.get("date","")
        people= int(request.form.get("people") or 1)
        notes = request.form.get("notes","").strip()
        payment_status = request.form.get("payment_status","unpaid")
        cur.execute("""UPDATE bookings SET
                       name=?, email=?, phone=?, trip=?, date=?, people=?, notes=?, payment_status=?
                       WHERE id=?""",
                    (name,email,phone,trip,date,people,notes,payment_status,bid))
        con.commit(); flash("تم حفظ التعديلات", "success")
        return redirect(url_for("admin_edit", bid=bid))
    return render_template("admin_edit.html", b=b)

@app.route("/admin/payments")
def admin_payments():
    admin_required()
    q = (request.args.get("q") or "").strip()
    page = max(int(request.args.get("page", 1)), 1); per = 30; off = (page-1)*per
    con = get_db(); cur = con.cursor()
    if q:
        like = f"%{q}%"
        cur.execute("""SELECT id,booking_id,gateway,payment_id,status,amount,currency,created_at
                       FROM payments
                       WHERE gateway LIKE ? OR status LIKE ? OR payment_id LIKE ? OR CAST(booking_id AS TEXT) LIKE ?
                       ORDER BY created_at DESC LIMIT ? OFFSET ?""",
                    (like, like, like, like, per, off))
        total = con.execute("""SELECT COUNT(*) FROM payments
                               WHERE gateway LIKE ? OR status LIKE ? OR payment_id LIKE ? OR CAST(booking_id AS TEXT) LIKE ?""",
                             (like, like, like, like)).fetchone()[0]
    else:
        cur.execute("""SELECT id,booking_id,gateway,payment_id,status,amount,currency,created_at
                       FROM payments ORDER BY created_at DESC LIMIT ? OFFSET ?""", (per, off))
        total = con.execute("SELECT COUNT(*) FROM payments").fetchone()[0]
    rows = cur.fetchall(); pages = (total + per - 1)//per
    return render_template("admin_payments.html", payments=rows, page=page, pages=pages, q=q)

@app.route("/admin/reports")
def admin_reports():
    admin_required()
    con = get_db(); cur = con.cursor()
    cur.execute("""
        SELECT strftime('%Y-%m', created_at) AS ym,
               COUNT(*),
               SUM(CASE WHEN status='paid' THEN amount ELSE 0 END)
        FROM payments GROUP BY ym ORDER BY ym DESC
    """)
    monthly = cur.fetchall()
    cur.execute("""
        SELECT b.trip,
               COUNT(p.id) AS cnt,
               SUM(CASE WHEN p.status='paid' THEN p.amount ELSE 0 END) AS sum_paid
        FROM bookings b
        LEFT JOIN payments p ON p.booking_id=b.id
        GROUP BY b.trip
        ORDER BY sum_paid DESC
    """)
    by_trip = cur.fetchall()
    return render_template("admin_reports.html", monthly=monthly, by_trip=by_trip)

# -----------------------------------------------------------------------------
# صفحات أخطاء
# -----------------------------------------------------------------------------
@app.errorhandler(404)
def e404(e): return render_template("404.html"), 404
@app.errorhandler(500)
def e500(e): return render_template("500.html"), 500
    
# --- ضع هذا الراوت في أي مكان بعد إنشاء app ---
@app.route('/service-worker.js')
def service_worker():
    # لو تضع الملف في static/js/service-worker.js
    sw_path = os.path.join(app.static_folder, 'js')
    return send_from_directory(sw_path, 'service-worker.js', mimetype='application/javascript')

# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)