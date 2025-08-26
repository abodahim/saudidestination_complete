# main.py
# -*- coding: utf-8 -*-

import os
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, send_from_directory, jsonify, make_response
)

# ========= إعداد التطبيق =========
app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")

# رقم نسخة لكسر كاش الأصول (غيّره من متغير بيئة على Render عند كل نشر)
ASSET_VER = os.environ.get("ASSET_VER", "3")

# ========= بيانات ثابتة (تجريبية) =========

CURRENCY = "ر.س"

TRIPS = [
    {
        "id": 1,
        "name": "رحلة جدة",
        "city": "جدة",
        "days": 1,
        "price": 299,
        "image": "images/jeddah_1.JPG",
        "excerpt": "اكتشف كورنيش جدة ومعالمها.",
        "content": "جولة على الكورنيش، البلد، وبعض المعالم الحديثة."
    },
    {
        "id": 2,
        "name": "رحلة الرياض",
        "city": "الرياض",
        "days": 1,
        "price": 349,
        "image": "images/riyadh_1.JPG",
        "excerpt": "تاريخ وثقافة العاصمة.",
        "content": "الدرعية، المتحف الوطني، ومناطق تراثية."
    },
    {
        "id": 3,
        "name": "رحلة ينبع",
        "city": "ينبع",
        "days": 1,
        "price": 399,
        "image": "images/yanbu_1.JPG",
        "excerpt": "شواطئ وأنشطة بحرية.",
        "content": "سباحة، سنوركلنغ، وجلسات على الشاطئ."
    },
    {
        "id": 4,
        "name": "رحلة العلا",
        "city": "العلا",
        "days": 2,
        "price": 899,
        "image": "images/alula_1.JPG",
        "excerpt": "عراقة الطبيعة والتاريخ.",
        "content": "مدائن صالح، مسارات مشي، وتجربة ليلية مذهلة."
    },
]

GUIDES = [
    {"name": "سامي الحربي",   "city": "الرياض", "years": 7, "photo": "images/guide1.PNG"},
    {"name": "عماد العتيبي",  "city": "جدة",   "years": 5, "photo": "images/guide2.PNG"},
    {"name": "ناصر المطيري",  "city": "الدمام", "years": 6, "photo": "images/guide3.PNG"},
    {"name": "فهد الشهري",    "city": "الطائف", "years": 4, "photo": "images/guide4.PNG"},
]

# تقييمات وهمية
REVIEWS = [
    {"name": "عبدالله", "rating": 5, "text": "تنظيم رائع والمرشد محترف.", "trip_id": 2},
    {"name": "محمد",   "rating": 4, "text": "تجربة جميلة والأسعار مناسبة.", "trip_id": 1},
    {"name": "سعد",    "rating": 5, "text": "العلا ساحرة، أوصي بها.", "trip_id": 4},
]

# أسئلة شائعة
FAQS = [
    {"q": "هل الأسعار تشمل المواصلات؟", "a": "نعم، تشمل النقل الداخلي المذكور في تفاصيل الرحلة."},
    {"q": "هل يمكن تغيير تاريخ الرحلة؟", "a": "نعم قبل 48 ساعة حسب التوفّر."},
    {"q": "ما وسائل الدفع المقبولة؟", "a": "بطاقات مدى/فيزا/ماستر كارد والتحويل البنكي."},
]

# عداد محجوزات (يبدأ بـ 3 كما طلبت)
BOOKED_COUNT = 3

# ========= أدوات مساعدة =========

def find_trip(tid: int):
    return next((t for t in TRIPS if t["id"] == tid), None)

def get_booked_count():
    return BOOKED_COUNT

def try_send_email(to_email: str, subject: str, body: str):
    """
    يرسل بريدًا فقط إذا كانت متغيرات البيئة متوفرة.
    لا يرفع خطأ عند الفشل حتى لا يعطل التجربة.
    """
    host = os.environ.get("SMTP_HOST")
    port = os.environ.get("SMTP_PORT")
    username = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASS")
    sender = os.environ.get("SMTP_SENDER", username)

    if not all([host, port, username, password, sender, to_email]):
        return False  # إعدادات غير مكتملة

    try:
        import smtplib
        from email.mime.text import MIMEText
        msg = MIMEText(body, _charset="utf-8")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to_email
        with smtplib.SMTP_SSL(host, int(port)) as s:
            s.login(username, password)
            s.sendmail(sender, [to_email], msg.as_string())
        return True
    except Exception:
        return False

def build_booking_pdf(data: dict):
    """
    يحاول إنشاء PDF (باستخدام reportlab إذا كان متوفرًا).
    إن لم يتوفر، يرجع ملف نصي كبديل، لكن بامتداد .pdf ومحتوى نصي واضح.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from io import BytesIO

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        textobject = c.beginText(40, 800)
        textobject.setFont("Helvetica", 12)
        lines = [
            "تأكيد حجز — وجهة السعودية",
            "----------------------------",
            f"الاسم: {data.get('name','')}",
            f"البريد: {data.get('email','')}",
            f"الجوال: {data.get('phone','')}",
            f"الرحلة: {data.get('trip_name','')}",
            f"عدد الأيام: {data.get('days','')}",
            f"المبلغ: {data.get('amount','')} {CURRENCY}",
            f"الحالة: {data.get('status','')}",
            f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        ]
        for line in lines:
            textobject.textLine(line)
        c.drawText(textobject)
        c.showPage()
        c.save()
        pdf = buffer.getvalue()
        buffer.close()
        resp = make_response(pdf)
        resp.headers["Content-Type"] = "application/pdf"
        resp.headers["Content-Disposition"] = "attachment; filename=booking.pdf"
        return resp
    except Exception:
        # بديل نصي بسيط
        txt = (
            "تأكيد حجز — وجهة السعودية\n"
            "----------------------------\n"
            f"الاسم: {data.get('name','')}\n"
            f"البريد: {data.get('email','')}\n"
            f"الجوال: {data.get('phone','')}\n"
            f"الرحلة: {data.get('trip_name','')}\n"
            f"عدد الأيام: {data.get('days','')}\n"
            f"المبلغ: {data.get('amount','')} {CURRENCY}\n"
            f"الحالة: {data.get('status','')}\n"
            f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        )
        resp = make_response(txt.encode("utf-8"))
        resp.headers["Content-Type"] = "application/pdf"
        resp.headers["Content-Disposition"] = "attachment; filename=booking.txt.pdf"
        return resp

# ========= معالجات القوالب/المتغيرات العمومية =========

@app.context_processor
def inject_globals():
    return dict(
        ASSET_VER=ASSET_VER,
        CURRENCY=CURRENCY,
        get_trip=find_trip,
        booked_count=get_booked_count(),
        trips_count=len(TRIPS),
        guides_count=len(GUIDES),
    )

# ========= المسارات الأساسية =========

@app.route("/")
def home():
    # ثلاثة مرشدين فقط للواجهة
    guides_preview = GUIDES[:3]
    return render_template("home.html", guides_preview=guides_preview)

@app.route("/trips")
def trips():
    return render_template("trips.html", trips=TRIPS)

@app.route("/trips/<int:trip_id>")
def trip_details(trip_id):
    trip = find_trip(trip_id)
    if not trip:
        flash("الرحلة غير موجودة.", "error")
        return redirect(url_for("trips"))
    return render_template("trip_details.html", trip=trip)

@app.route("/guides")
def guides():
    return render_template("guides.html", guides=GUIDES)

@app.route("/reviews")
def reviews():
    return render_template("reviews.html", reviews=REVIEWS, trips=TRIPS)

@app.route("/faq")
def faq():
    return render_template("faq.html", faqs=FAQS)

@app.route("/cancellation")
def cancellation_policy():
    return render_template("cancellation.html")

# ========= الحجز + الدفع الوهمي + التأكيد =========

@app.route("/booking", methods=["GET", "POST"])
def booking():
    global BOOKED_COUNT
    if request.method == "POST":
        name  = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        trip_id = int(request.form.get("trip_id", "0"))
        days = int(request.form.get("days", "1"))

        trip = find_trip(trip_id)
        if not trip:
            flash("الرجاء اختيار رحلة صحيحة.", "error")
            return redirect(url_for("booking"))

        # حساب المبلغ
        amount = trip["price"] * max(1, min(days, 7))

        # (وهمي) توجيه لصفحة دفع بسيطة
        return redirect(url_for("pay", name=name, email=email, phone=phone,
                                trip_id=trip_id, days=days, amount=amount))
    return render_template("booking.html", trips=TRIPS)

@app.route("/pay")
def pay():
    """
    بوابة دفع وهمية: تضغط "إتمام الدفع" بواجهة HTML بسيطة (ضمن قالب booking_confirm).
    في مشروع إنتاجي تربط Stripe/Tabby/Moyasar إلخ.
    """
    name   = request.args.get("name", "")
    email  = request.args.get("email", "")
    phone  = request.args.get("phone", "")
    trip_id= int(request.args.get("trip_id", "0"))
    days   = int(request.args.get("days", "1"))
    amount = float(request.args.get("amount", "0"))
    trip = find_trip(trip_id)
    if not trip:
        flash("بيانات الدفع غير صحيحة.", "error")
        return redirect(url_for("booking"))
    return render_template("booking_confirm.html",
                           step="pay",
                           data=dict(name=name, email=email, phone=phone,
                                     trip_id=trip_id, days=days, amount=amount),
                           trip=trip)

@app.route("/confirm", methods=["POST"])
def confirm():
    """
    يُنادى بعد 'الدفع'، يزيد عداد الحجوزات، يرسل بريدًا (إن وُجد SMTP)،
    ويعرض صفحة تأكيد مع زر تنزيل PDF وبيانات التواصل.
    """
    global BOOKED_COUNT
    name   = request.form.get("name", "")
    email  = request.form.get("email", "")
    phone  = request.form.get("phone", "")
    trip_id= int(request.form.get("trip_id", "0"))
    days   = int(request.form.get("days", "1"))
    amount = float(request.form.get("amount", "0"))

    trip = find_trip(trip_id)
    if not trip:
        flash("لم يتم العثور على الرحلة.", "error")
        return redirect(url_for("booking"))

    BOOKED_COUNT += 1

    # بريد تأكيد (اختياري)
    subject = "تأكيد حجز — وجهة السعودية"
    body = (f"مرحبًا {name},\n\n"
            f"تم استلام حجزك بنجاح.\n"
            f"الرحلة: {trip['name']}\n"
            f"عدد الأيام: {days}\n"
            f"المبلغ: {amount} {CURRENCY}\n\n"
            "شكرًا لاختيارك وجهة السعودية.")
    try_send_email(email, subject, body)

    return render_template("booking_confirm.html",
                           step="done",
                           trip=trip,
                           data=dict(name=name, email=email, phone=phone,
                                     trip_id=trip_id, days=days, amount=amount,
                                     status="مدفوع"))

@app.route("/booking/pdf")
def booking_pdf():
    """
    إنشاء ملف PDF لنتيجة آخر عملية (يُمرر كل شيء بالـ querystring).
    """
    data = {
        "name":  request.args.get("name",""),
        "email": request.args.get("email",""),
        "phone": request.args.get("phone",""),
        "trip_name": request.args.get("trip_name",""),
        "days":  request.args.get("days",""),
        "amount":request.args.get("amount",""),
        "status":request.args.get("status",""),
    }
    return build_booking_pdf(data)

# ========= ملفات ثابتة إضافية =========

@app.route("/manifest.webmanifest")
def manifest():
    # الملف داخل static/manifest.webmanifest
    return send_from_directory("static", "manifest.webmanifest",
                               mimetype="application/manifest+json")

# ========= معالجات أخطاء بسيطة =========

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="الصفحة غير موجودة"), 404

@app.errorhandler(500)
def server_error(e):
    # يُفضّل في Render تفقد الـ logs عند ظهور 500
    return render_template("error.html", code=500, message="خطأ داخلي في الخادم"), 500

# ========= تشغيل محلي =========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)