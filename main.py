import os, uuid, smtplib
from email.message import EmailMessage
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, send_from_directory, session, abort, make_response
)

# محاولة تفعيل PDF عبر WeasyPrint إن كانت منصّبة
WEASYPRINT_AVAILABLE = False
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except Exception:
    WEASYPRINT_AVAILABLE = False

app = Flask(
    __name__,
    static_url_path="/static",
    static_folder="static",
    template_folder="templates",
)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret")

# ====== إعدادات البريد من البيئة ======
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))  # TLS
EMAIL_USER = os.getenv("EMAIL_USER")              # مثال: aboodahim@gmail.com
EMAIL_PASS = os.getenv("EMAIL_PASS")              # App Password
EMAIL_FROM = os.getenv("EMAIL_FROM", EMAIL_USER)  # غالبًا نفس الحساب
EMAIL_BCC  = os.getenv("EMAIL_BCC")               # اختياري: نسخة خفية إدارية
BASE_URL   = os.getenv("BASE_URL")                # مثال: https://...onrender.com

def send_email(to_email: str, subject: str, html_body: str, text_body: str = None, bcc: str = None, attachments=None):
    """إرسال بريد عبر SMTP باستخدام TLS، مع دعم BCC ومرفقات."""
    if not all([EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, EMAIL_FROM]):
        print("Email settings missing; skipping email send.")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"]    = EMAIL_FROM
    msg["To"]      = to_email
    if bcc:
        msg["Bcc"] = bcc

    if not text_body:
        text_body = "تم تأكيد حجزك بنجاح."
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    # مرفقات (قائمة من dict: {"filename":..., "data": bytes, "mime": "application/pdf"})
    if attachments:
        for att in attachments:
            fname = att.get("filename", "attachment")
            data  = att.get("data", b"")
            mime  = att.get("mime", "application/octet-stream")
            maintype, _, subtype = mime.partition("/")
            msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=fname)

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print("Email send error:", e)
        return False

# ====== بيانات الرحلات والمرشدين ======
TRIPS = [
    {"id": 1, "name": "رحلة جدة",   "default_guide_id": 1},
    {"id": 2, "name": "رحلة الرياض", "default_guide_id": 2},
    {"id": 3, "name": "رحلة ينبع",   "default_guide_id": 3},
]

GUIDES = [
    {"id": 1, "name": "أحمد السبيعي", "city": "جدة",   "phone": "+966500000001", "whatsapp": "+966500000001", "img": "images/guide1.PNG"},
    {"id": 2, "name": "سارة العتيبي", "city": "الرياض", "phone": "+966500000002", "whatsapp": "+966500000002", "img": "images/guide1.PNG"},
    {"id": 3, "name": "خالد الزهراني","city": "الجنوب", "phone": "+966500000003", "whatsapp": "+966500000003", "img": "images/guide1.PNG"},
]

def get_trip(trip_id):
    return next((t for t in TRIPS if str(t["id"]) == str(trip_id)), None)

def get_guide(guide_id):
    return next((g for g in GUIDES if str(g["id"]) == str(guide_id)), None)

# حافظات للجلسة
def get_pending():
    return session.setdefault("pending_bookings", {})

def get_confirmed():
    return session.setdefault("confirmed_bookings", {})

# ===========================
# الصفحات العامة
# ===========================
@app.route("/")
def home():
    return render_template("home.html", active="home", trips=TRIPS, guides=GUIDES)

@app.route("/trips")
def trips():
    return render_template("trips.html", active="trips", trips=TRIPS)

@app.route("/trips/<int:trip_id>")
def trip_details(trip_id):
    trip = get_trip(trip_id)
    if not trip:
        abort(404)
    return render_template("trip_details.html", trip_id=trip_id, trip=trip, active="trips")

@app.route("/guides")
def guides():
    return render_template("guides.html", active="guides", guides=GUIDES)

@app.route("/gallery")
def gallery():
    return render_template("gallery.html", active="gallery")

@app.route("/reviews")
def reviews():
    return render_template("reviews.html", active="reviews")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        _name = request.form.get("name", "").strip()
        _email = request.form.get("email", "").strip()
        _msg = request.form.get("message", "").strip()
        flash("تم استلام رسالتك بنجاح، وسنعاود التواصل قريبًا.", "success")
        return redirect(url_for("thank_you"))
    return render_template("contact.html", active="contact")

# ===========================
# الحجز والدفع والإيصال
# ===========================
@app.route("/booking", methods=["GET", "POST"])
@app.route("/book", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip()
        phone    = request.form.get("phone", "").strip()
        trip_id  = request.form.get("trip_id", "").strip()
        guide_id = request.form.get("guide_id", "").strip()

        if not all([name, email, phone, trip_id]):
            flash("الرجاء تعبئة جميع الحقول المطلوبة.", "danger")
            return redirect(url_for("booking"))

        trip = get_trip(trip_id)
        if not trip:
            flash("الرحلة غير موجودة.", "danger")
            return redirect(url_for("booking"))

        if not guide_id:
            guide_id = trip["default_guide_id"]

        guide = get_guide(guide_id)
        if not guide:
            flash("المرشد غير موجود.", "danger")
            return redirect(url_for("booking"))

        booking_id = uuid.uuid4().hex[:8].upper()

        pending = get_pending()
        pending[booking_id] = {
            "booking_id": booking_id,
            "name": name,
            "email": email,
            "phone": phone,
            "trip_id": trip["id"],
            "trip_name": trip["name"],
            "guide_id": guide["id"],
        }
        session["pending_bookings"] = pending

        flash("تم إنشاء الحجز، انتقل إلى الدفع لإكمال العملية.", "success")
        return redirect(url_for("payment", booking_id=booking_id))

    # GET — prefill
    selected_trip_id  = request.args.get("trip_id", "")
    selected_guide_id = request.args.get("guide_id", "")
    return render_template(
        "booking.html",
        active="booking",
        trips=TRIPS,
        guides=GUIDES,
        selected_trip_id=selected_trip_id,
        selected_guide_id=selected_guide_id
    )

@app.route("/payment", methods=["GET", "POST"])
def payment():
    booking_id = request.args.get("booking_id", "").strip() or request.form.get("booking_id", "").strip()
    pending = get_pending()
    booking = pending.get(booking_id) if booking_id else None

    if not booking:
        flash("لا يوجد حجز صالح للدفع.", "danger")
        return redirect(url_for("booking"))

    if request.method == "POST":
        # (تجريبي) يعتبر الدفع ناجحًا
        confirmed = get_confirmed()
        confirmed[booking_id] = booking
        session["confirmed_bookings"] = confirmed

        # إزالة من المعلّقة
        pending.pop(booking_id, None)
        session["pending_bookings"] = pending

        # توليد رابط الإيصال
        try:
            receipt_url = url_for("receipt", booking_id=booking_id, _external=True)
        except Exception:
            receipt_url = f"{BASE_URL}/receipt/{booking_id}" if BASE_URL else f"/receipt/{booking_id}"

        # تجهيز مرفق الفاتورة PDF (إذا توفّر WeasyPrint)
        attachments = []
        invoice_html = render_template("invoice_print.html", booking=booking, trip=get_trip(booking["trip_id"]), guide=get_guide(booking["guide_id"]))
        if WEASYPRINT_AVAILABLE:
            try:
                pdf_bytes = HTML(string=invoice_html, base_url=BASE_URL or "").write_pdf()
                attachments.append({"filename": f"invoice_{booking_id}.pdf", "data": pdf_bytes, "mime": "application/pdf"})
            except Exception as e:
                print("PDF generation error:", e)

        # إرسال بريد تأكيد + BCC إداري (إن وُجِد)
        html_body = render_template("emails/receipt_email.html", booking=booking, receipt_url=receipt_url)
        text_body = render_template("emails/receipt_email.txt",   booking=booking, receipt_url=receipt_url)
        sent = send_email(
            to_email=booking["email"],
            subject=f"تأكيد حجزك #{booking_id} - وجهة السعودية",
            html_body=html_body,
            text_body=text_body,
            bcc=EMAIL_BCC,
            attachments=attachments
        )
        if not sent:
            flash("تم الدفع، وتعذّر إرسال البريد (تأكد من إعدادات البريد).", "danger")
        else:
            flash("تمت عملية الدفع وأُرسل تأكيد إلى بريدك.", "success")

        return redirect(url_for("receipt", booking_id=booking_id))

    # GET: عرض صفحة الدفع
    return render_template("payment.html", active="payment", booking=booking)

@app.route("/receipt/<string:booking_id>")
def receipt(booking_id):
    confirmed = get_confirmed()
    booking = confirmed.get(booking_id)
    if not booking:
        return render_template("receipt_locked.html", booking_id=booking_id), 200

    trip = get_trip(booking["trip_id"])
    guide = get_guide(booking["guide_id"])
    return render_template("receipt.html", booking=booking, trip=trip, guide=guide, active=None)

# تنزيل الفاتورة (HTML/PDF) — يظهر الرابط فقط في صفحة الإيصال المدفوع
@app.route("/invoice/<string:booking_id>/download")
def download_invoice(booking_id):
    confirmed = get_confirmed()
    booking = confirmed.get(booking_id)
    if not booking:
        abort(403)

    trip  = get_trip(booking["trip_id"])
    guide = get_guide(booking["guide_id"])

    fmt = request.args.get("fmt", "pdf").lower()
    html = render_template("invoice_print.html", booking=booking, trip=trip, guide=guide)

    if fmt == "html" or not WEASYPRINT_AVAILABLE:
        resp = make_response(html)
        resp.headers["Content-Type"] = "text/html; charset=utf-8"
        resp.headers["Content-Disposition"] = f'attachment; filename=invoice_{booking_id}.html'
        return resp

    # PDF عبر WeasyPrint
    pdf_bytes = HTML(string=html, base_url=BASE_URL or "").write_pdf()
    resp = make_response(pdf_bytes)
    resp.headers["Content-Type"] = "application/pdf"
    resp.headers["Content-Disposition"] = f'attachment; filename=invoice_{booking_id}.pdf'
    return resp

@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html", active=None)

# ===========================
# الدخول والإدارة (مبدئي)
# ===========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") == "admin" and request.form.get("password") == "admin":
            flash("تم تسجيل الدخول.", "success")
            return redirect(url_for("admin_dashboard"))
        flash("بيانات الدخول غير صحيحة.", "danger")
    return render_template("login.html", active=None)

@app.route("/admin")
def admin_dashboard():
    return render_template("admin_dashboard.html", active=None)

# ===========================
# ملفات ثابتة مطلوبة
# ===========================
@app.route("/service-worker.js")
def service_worker():
    return send_from_directory("static", "service-worker.js", mimetype="application/javascript")

@app.route("/manifest.webmanifest")
def manifest():
    return send_from_directory("static", "manifest.webmanifest", mimetype="application/manifest+json")

@app.route("/robots.txt")
def robots():
    return send_from_directory("static", "robots.txt", mimetype="text/plain")

# ===========================
# تشغيل
# ===========================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)