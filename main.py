# main.py
import os
from io import BytesIO
from datetime import datetime
import ssl
import smtplib
from email.message import EmailMessage

import requests
import stripe

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, abort, jsonify, send_file
)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("APP_SECRET_KEY", "change_this_secret_key")
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.jinja_env.auto_reload = True
# ===== مزوّد الدفع واعداداته (Render env) =====
PAY_PROVIDER = os.getenv("PAY_PROVIDER", "MOYASAR").strip().upper()  # MOYASAR أو STRIPE

# MOYASAR
MOYASAR_SECRET_KEY      = os.getenv("MOYASAR_SECRET_KEY", "").strip()
MOYASAR_PUBLISHABLE_KEY = os.getenv("MOYASAR_PUBLISHABLE_KEY", "").strip()
SITE_BASE_URL           = os.getenv("SITE_BASE_URL", "http://localhost:5000").strip()

# STRIPE
STRIPE_SECRET_KEY      = os.getenv("STRIPE_SECRET_KEY", "").strip()
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "").strip()
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# ===== إعدادات البريد (Render env) =====
SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))  # 587 TLS (starttls)
SMTP_USER = os.getenv("SMTP_USER", "").strip()
SMTP_PASS = os.getenv("SMTP_PASS", "").strip()
MAIL_FROM = os.getenv("MAIL_FROM", "no-reply@example.com").strip()
MAIL_BCC  = os.getenv("MAIL_BCC", "").strip()  # اختياري (إدارة)

# ===== تيليجرام للإشعارات =====
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# ===== السنة في كل القوالب =====
@app.context_processor
def inject_current_year():
    return {"current_year": datetime.now().year}

# ===== بيانات الرحلات (صور داخل static/images/) =====
TRIPS = [
    {
        "slug": "jeddah",
        "title": "رحلة جدة",
        "city": "جدة",
        "summary": "استمتع بالكورنيش والمعالم التاريخية في جدة.",
        "images": ["images/jeddah_1.JPG", "images/jeddah_2.JPG"],
        "price_per_day": 450,
        "days_default": 3,
    },
    {
        "slug": "riyadh",
        "title": "رحلة الرياض",
        "city": "الرياض",
        "summary": "اكتشف معالم العاصمة وتجارب حديثة.",
        "images": ["images/riyadh_1.JPG", "images/riyadh_2.JPG"],
        "price_per_day": 500,
        "days_default": 2,
    },
    {
        "slug": "alula",
        "title": "رحلة العلا",
        "city": "العلا",
        "summary": "جبال ساحرة ومواقع تراثية وتجارب صحراوية فريدة.",
        "images": ["images/ala_1.JPG", "images/ala_2.JPG"],
        "price_per_day": 650,
        "days_default": 2,
    },
    {
        "slug": "yanbu",
        "title": "رحلة ينبع",
        "city": "ينبع",
        "summary": "شواطئ خلابة وأنشطة بحرية ممتعة.",
        "images": ["images/yanbu_1.JPG", "images/yanbu_2.JPG"],
        "price_per_day": 400,
        "days_default": 2,
    },
]

def get_trip(slug):
    return next((t for t in TRIPS if t["slug"] == slug), None)

# ===== أدوات الإشعارات =====
def send_email(to_email, subject, body, reply_to=None):
    """يرسل بريدًا عبر SMTP (TLS على 587) إن كانت إعدادات SMTP مضبوطة."""
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS and MAIL_FROM and to_email):
        return
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = MAIL_FROM
    msg["To"] = to_email
    if reply_to:
        msg["Reply-To"] = reply_to
    if MAIL_BCC:
        msg["Bcc"] = MAIL_BCC
    msg.set_content(body)
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
    except Exception as exc:
        print("[email] failed:", exc)

def send_telegram(text):
    """يرسل رسالة تيليجرام إن كانت متغيرات تيليجرام مضبوطة."""
    if not (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
    except Exception as exc:
        print("[telegram] failed:", exc)

# =========================
# صفحات عامة
# =========================
@app.route("/")
def home():
    stats = {"guides_count": 4, "trips_available": len(TRIPS), "booked": 3}
    guides = [
        {"name": "سامي الحربي", "city": "الرياض", "years": 7, "photo": "images/guide1.PNG"},
        {"name": "ماجد المطيري", "city": "جدة",   "years": 5, "photo": "images/guide2.PNG"},
        {"name": "عبدالعزيز الدوسري", "city": "ينبع", "years": 6, "photo": "images/guide3.PNG"},
    ]
    reviews = [
        {"name": "أبو خالد", "rating": 5, "text": "تنظيم ممتاز وخدمة رائعة."},
        {"name": "سلمان",   "rating": 4, "text": "البرنامج ممتع والأسعار مناسبة."},
        {"name": "نايف",    "rating": 5, "text": "تجربة لا تُنسى في العلا."},
    ]
    return render_template("home.html", trips=TRIPS[:3], guides=guides, stats=stats, reviews=reviews)

@app.route("/trips")
def trips():
    return render_template("trips.html", trips=TRIPS)

@app.route("/trip/<slug>")
def trip_detail(slug):
    trip = get_trip(slug)
    if not trip:
        abort(404)
    return render_template("trip_detail.html", trip=trip)

@app.route("/guides")
def guides_page():
    guides = [
        {"name": "سامي الحربي", "city": "الرياض", "years": 7, "photo": "images/guide1.PNG"},
        {"name": "ماجد المطيري", "city": "جدة",   "years": 5, "photo": "images/guide2.PNG"},
        {"name": "عبدالعزيز الدوسري", "city": "ينبع", "years": 6, "photo": "images/guide3.PNG"},
        {"name": "فهد الشهري", "city": "العلا",  "years": 8, "photo": "images/guide4.PNG"},
    ]
    return render_template("guides.html", guides=guides)

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/reviews")
def reviews():
    reviews = [
        {"name": "أبو خالد", "rating": 5, "text": "تنظيم ممتاز وخدمة رائعة."},
        {"name": "سلمان",   "rating": 4, "text": "البرنامج ممتع والأسعار مناسبة."},
        {"name": "نايف",    "rating": 5, "text": "تجربة لا تُنسى في العلا."},
    ]
    return render_template("reviews.html", reviews=reviews)

@app.route("/faq")
def faq():
    faqs = [
        {"q": "كيف أحجز رحلة؟", "a": "من صفحة الحجز اختر الرحلة والأيام ثم أكمل البيانات."},
        {"q": "هل يمكنني استرداد المبلغ؟", "a": "يمكن الإلغاء قبل 48 ساعة واسترداد 80%."},
        {"q": "هل تشمل الأسعار الوجبات؟", "a": "تختلف حسب الرحلة، التفاصيل داخل كل رحلة."},
    ]
    return render_template("faq.html", faqs=faqs)

@app.route("/cancellation")
def cancellation():
    return render_template("cancellation.html")

# =========================
# الحجز (GET/POST)
# =========================
@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "GET":
        selected_slug = request.args.get("trip")
        return render_template("booking.html", trips=TRIPS, selected_slug=selected_slug)

    # --- POST ---
    name   = (request.form.get("name") or "").strip()
    email  = (request.form.get("email") or "").strip()
    phone  = (request.form.get("phone") or "").strip()
    slug   = (request.form.get("trip") or "").strip()
    days_s = (request.form.get("days") or "1").strip()
    date   = (request.form.get("date") or "").strip()
    pers_s = (request.form.get("persons") or "1").strip()
    agree  = request.form.get("agree")

    trip = get_trip(slug) if slug else None
    try:
        days = max(1, min(7, int(days_s)))
    except ValueError:
        days = 1
    try:
        persons = max(1, int(pers_s))
    except ValueError:
        persons = 1

    if not (name and email and phone and trip and agree):
        flash("يرجى استكمال جميع الحقول والموافقة على سياسة الإلغاء.", "danger")
        return redirect(url_for("booking", trip=slug or None))

    # إجمالي السعر: اليوم × الأيام × الأشخاص
    total_price = days * trip["price_per_day"] * persons

    # تخزين ملخص الحجز في الجلسة
    session["last_booking"] = {
        "name": name,
        "email": email,
        "phone": phone,
        "trip": {
            "slug": trip["slug"],
            "title": trip["title"],
            "city": trip["city"],
            "price_per_day": trip["price_per_day"],
        },
        "days": days,
        "persons": persons,
        "date": date,
        "total_price": total_price,
        "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    }
    session["paid"] = False

    # إشعار إداري مبدئي (قيد الدفع)
    admin_text = (
        f"🧾 طلب حجز جديد (قيد الدفع)\n"
        f"الرحلة: {trip['title']} ({trip['slug']})\n"
        f"الاسم: {name}\n"
        f"الإيميل: {email}\n"
        f"الجوال: {phone}\n"
        f"التاريخ: {date or '—'}\n"
        f"الأيام: {days} | الأشخاص: {persons}\n"
        f"الإجمالي: {total_price} SAR"
    )
    send_telegram(admin_text)
    if MAIL_BCC:
        send_email(MAIL_BCC, "طلب حجز جديد (قيد الدفع)", admin_text, reply_to=email or None)

    # التفرّع حسب مزوّد الدفع
    if PAY_PROVIDER == "MOYASAR":
        return redirect(url_for("pay_start"), code=303)

    elif PAY_PROVIDER == "STRIPE":
        if not STRIPE_SECRET_KEY or not STRIPE_PUBLISHABLE_KEY:
            return render_template(
                "error.html", code=500,
                message="بوابة Stripe غير مهيأة. اضبط STRIPE_SECRET_KEY و STRIPE_PUBLISHABLE_KEY."
            ), 500

        # Stripe لا يقبل metadata متداخلة — نفردها كسلاسل:
        md = {
            "trip_slug":   trip["slug"],
            "trip_title":  trip["title"],
            "trip_city":   trip["city"],
            "price_per_day": str(trip["price_per_day"]),
            "name": name, "email": email, "phone": phone,
            "date": date, "days": str(days), "persons": str(persons),
            "total_sar": str(total_price),
            "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        }

        unit_amount_sar = trip["price_per_day"]
        quantity = days * persons

        checkout_session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            customer_email=email or None,
            line_items=[{
                "quantity": quantity,
                "price_data": {
                    "currency": "sar",
                    "unit_amount": int(unit_amount_sar * 100),
                    "product_data": {
                        "name": f"حجز {trip['title']} — {days} يوم × {persons} شخص",
                        "description": f"تاريخ الرحلة: {date or '—'}",
                    },
                },
            }],
            metadata=md,
            success_url=url_for("book_success", _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=url_for("booking", _external=True),
        )
        return redirect(checkout_session.url, code=303)

    else:
        flash("بوابة الدفع غير مهيأة.", "danger")
        return redirect(url_for("book_success"))

# =========================
# صفحة النجاح بعد الدفع
# =========================
@app.route("/book_success")
def book_success():
    # دعم Stripe (session_id) أو Moyasar (session["paid"])
    paid = bool(session.get("paid"))
    details = session.get("last_booking", {})
    session_id = request.args.get("session_id")

    # تحقق Stripe
    if session_id and STRIPE_SECRET_KEY:
        try:
            sess = stripe.checkout.Session.retrieve(session_id)
            if sess.get("payment_status") == "paid":
                paid = True
                # خزّن علم الدفع حتى تظهر مزايا ما بعد الدفع
                session["paid"] = True

                # تفاصيل من metadata (مسطّحة كسلاسل)
                md = sess.get("metadata", {}) or {}
                # حاول تحديث session["last_booking"] من metadata (اختياري)
                if md:
                    try:
                        session["last_booking"] = {
                            "name": md.get("name") or details.get("name"),
                            "email": md.get("email") or details.get("email"),
                            "phone": md.get("phone") or details.get("phone"),
                            "trip": {
                                "slug": md.get("trip_slug") or details.get("trip", {}).get("slug"),
                                "title": md.get("trip_title") or details.get("trip", {}).get("title"),
                                "city": md.get("trip_city") or details.get("trip", {}).get("city"),
                                "price_per_day": int(md.get("price_per_day") or details.get("trip", {}).get("price_per_day") or 0),
                            },
                            "days": int(md.get("days") or details.get("days") or 1),
                            "persons": int(md.get("persons") or details.get("persons") or 1),
                            "date": md.get("date") or details.get("date") or "",
                            "total_price": int(float(md.get("total_sar") or details.get("total_price") or 0)),
                            "created_at": md.get("created_at") or details.get("created_at") or "",
                        }
                        details = session["last_booking"]
                    except Exception:
                        pass

                # أرسل تأكيد (مرة واحدة)
                try:
                    data = session.get("last_booking") or details
                    if data:
                        confirm_text = (
                            f"✅ تم تأكيد الحجز\n"
                            f"الرحلة: {data['trip']['title']}\n"
                            f"الاسم: {data['name']}\n"
                            f"الإيميل: {data['email']}\n"
                            f"الجوال: {data['phone']}\n"
                            f"الإجمالي: {data['total_price']} ر.س"
                        )
                        send_telegram(confirm_text)
                        send_email(
                            to_email=data["email"],
                            subject="تأكيد الحجز — وجهة السعودية",
                            body=(
                                f"شكرًا لك {data['name']}!\n"
                                f"تم تأكيد حجزك لرحلة: {data['trip']['title']}.\n"
                                f"الإجمالي المدفوع: {data['total_price']} ر.س"
                            ),
                        )
                except Exception as exc:
                    print("[post-pay notify] error:", exc)

        except Exception as exc:
            print("[stripe retrieve] error:", exc)

    return render_template("book_success.html", paid=paid, details=details)

# =========================
# إنشاء PDF + إرسال بريد (لـ Moyasar بعد العودة)
# =========================
def build_invoice_pdf(data):
    """ينشئ PDF بسيط للفاتورة من بيانات الحجز."""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    y = h - 30*mm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(25*mm, y, "فاتورة حجز — وجهة السعودية")
    y -= 12*mm

    c.setFont("Helvetica", 11)
    lines = [
        f"الاسم: {data['name']}",
        f"البريد: {data['email']}",
        f"الجوال: {data['phone']}",
        f"الرحلة: {data['trip']['title']} — {data['trip']['city']}",
        f"عدد الأيام: {data['days']} | الأشخاص: {data['persons']}",
        f"السعر اليومي: {data['trip']['price_per_day']} ر.س",
        f"الإجمالي: {data['total_price']} ر.س",
        f"وقت الإنشاء: {data['created_at']}",
    ]
    for ln in lines:
        c.drawString(25*mm, y, ln)
        y -= 8*mm

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()

def send_email_with_optional_attachment(to_email, subject, body, attachment=None, filename="invoice.pdf"):
    """يرسل بريدًا عبر SMTP مع مرفق اختياري."""
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS and MAIL_FROM and to_email):
        print("[Email] SMTP not configured or no recipient; skipped sending.")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = MAIL_FROM
    msg["To"] = to_email
    if MAIL_BCC:
        msg["Bcc"] = MAIL_BCC
    msg.set_content(body)

    if attachment:
        msg.add_attachment(attachment, maintype="application", subtype="pdf", filename=filename)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls(context=ssl.create_default_context())
        smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)

@app.route("/invoice.pdf")
def invoice_pdf():
    data = session.get("last_booking")
    if not data:
        flash("لا يوجد حجز لعرض فاتورته.", "warning")
        return redirect(url_for("booking"))
    pdf_bytes = build_invoice_pdf(data)
    return send_file(BytesIO(pdf_bytes), as_attachment=True,
                     download_name="invoice.pdf", mimetype="application/pdf")

# =========================
# الدفع (Moyasar Hosted)
# =========================
def _amount_halalas(sar_amount):
    return int(float(sar_amount) * 100)

@app.route("/pay/start", methods=["GET", "POST"])
def pay_start():
    data = session.get("last_booking")
    if not data:
        flash("لا يوجد حجز لإتمام الدفع.", "warning")
        return redirect(url_for("booking"))

    if PAY_PROVIDER != "MOYASAR" or not MOYASAR_SECRET_KEY:
        flash("بوابة الدفع غير مهيأة.", "danger")
        return redirect(url_for("book_success"))

    amount = _amount_halalas(data["total_price"])
    callback_success = f"{SITE_BASE_URL}{url_for('pay_return')}?status=paid"
    callback_failed  = f"{SITE_BASE_URL}{url_for('pay_return')}?status=failed"

    url = "https://api.moyasar.com/v1/invoices"
    auth = (MOYASAR_SECRET_KEY, "")
    payload = {
        "amount": amount,
        "currency": "SAR",
        "description": f"حجز: {data['trip']['title']} - {data['name']} ({data['days']} يوم)",
        "callback_url": callback_success,   # إشعار سيرفر-إلى-سيرفر (لو مفعّل لديهم)
        "expired_at": None,
        "metadata": {
            "name": data["name"],
            "email": data["email"],
            "phone": data["phone"],
            "trip_slug": data["trip"]["slug"],
            "days": data["days"],
            "persons": data["persons"],
            "created_at": data["created_at"]
        },
        "return_url": callback_failed       # رجوع المتصفح للفشل
    }

    try:
        r = requests.post(url, auth=auth, json=payload, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print("Moyasar create invoice error:", e)
        flash("تعذّر إنشاء جلسة الدفع. حاول لاحقًا.", "danger")
        return redirect(url_for("book_success"))

    inv = r.json()
    pay_url = inv.get("url") or inv.get("invoice_url")
    if not pay_url:
        flash("لم نستلم رابط الدفع من المزود.", "danger")
        return redirect(url_for("book_success"))

    session["last_invoice_id"] = inv.get("id")
    return redirect(pay_url)

@app.route("/pay/return")
def pay_return():
    status = (request.args.get("status") or "failed").lower()
    if status == "paid":
        session["paid"] = True
        flash("تم الدفع بنجاح. شكرًا لك!", "success")

        # إرسال بريد تأكيد + إرفاق فاتورة PDF
        data = session.get("last_booking")
        if data:
            try:
                pdf = build_invoice_pdf(data)
                body = (
                    f"عميلنا العزيز {data['name']},\n\n"
                    f"تم استلام دفعك لحجز {data['trip']['title']} ({data['days']} يوم، {data['persons']} أشخاص).\n"
                    f"الإجمالي: {data['total_price']} ر.س.\n\n"
                    f"مرفق فاتورة PDF.\n"
                    f"شكرًا لاختيارك وجهة السعودية."
                )
                send_email_with_optional_attachment(
                    to_email=data["email"],
                    subject="تأكيد الحجز — وجهة السعودية",
                    body=body,
                    attachment=pdf,
                    filename="invoice.pdf"
                )
                # إشعار تيليجرام
                send_telegram(
                    f"✅ تم الدفع عبر Moyasar\nالاسم: {data['name']}\nالرحلة: {data['trip']['title']}\nالإجمالي: {data['total_price']} SAR"
                )
            except Exception as e:
                print("[Email/Telegram] error after Moyasar:", e)
    else:
        flash("لم يكتمل الدفع. يمكنك المحاولة مرة أخرى.", "warning")

    return redirect(url_for("book_success"))

@app.route("/pay/webhook", methods=["POST"])
def pay_webhook():
    try:
        event = request.get_json(force=True, silent=False)
    except Exception:
        return jsonify({"ok": False}), 400
    kind = event.get("event")
    obj  = event.get("data", {})
    status = (obj.get("status") or "").lower()
    invoice_id = obj.get("id") or obj.get("invoice_id")
    print(f"[Webhook] kind={kind} status={status} invoice={invoice_id}")
    return jsonify({"ok": True})

# ===== فافيكون + أخطاء =====
@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("images/favicon.png")

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="الصفحة غير موجودة"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="حدث خطأ داخلي في الخادم"), 500
    
@app.route("/ping")
def ping():
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)