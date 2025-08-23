import os, uuid
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, send_from_directory, session, abort
)

app = Flask(__name__, static_url_path="/static")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret")

# ====== بيانات الاتصال (تُستخدم بعد الدفع فقط) ======
CONTACT_PHONE = os.getenv("CONTACT_PHONE", "+966500000000")
CONTACT_WHATSAPP = os.getenv("CONTACT_WHATSAPP", "966500000000")

@app.context_processor
def inject_contact():
    return {
        "CONTACT_PHONE": CONTACT_PHONE,
        "CONTACT_WHATSAPP": CONTACT_WHATSAPP
    }

# ====== بيانات الرحلات الموحدة ======
TRIPS = {
    "1": {
        "id": "1",
        "slug": "jeddah",
        "name": "رحلة جدة",
        "city": "جدة",
        "price": 299,
        "days": 1,
        "short": "جولة مميزة على كورنيش جدة ومعالمها الحديثة.",
        "image": "images/jeddah_1.JPG",
        "gallery": ["images/jeddah_2.JPG", "images/jeddah_3.JPG", "images/jeddah_4.JPG"],
        "includes": ["مرشد سياحي", "مواصلات", "وجبة خفيفة"]
    },
    "2": {
        "id": "2",
        "slug": "riyadh",
        "name": "رحلة الرياض",
        "city": "الرياض",
        "price": 349,
        "days": 1,
        "short": "اكتشف تاريخ العاصمة ومعالمها التراثية.",
        "image": "images/riyadh_1.JPG",
        "gallery": ["images/riyadh_2.JPG", "images/riyadh_3.JPG", "images/riyadh_4.JPG"],
        "includes": ["مرشد سياحي", "تذاكر المتاحف", "مياه"]
    },
    "3": {
        "id": "3",
        "slug": "yanbu",
        "name": "رحلة ينبع",
        "city": "ينبع",
        "price": 399,
        "days": 1,
        "short": "استمتع بجمال الشواطئ والأنشطة البحرية في ينبع.",
        "image": "images/yanbu_1.JPG",
        "gallery": ["images/yanbu_2.JPG", "images/yanbu_3.JPG", "images/yanbu_4.JPG"],
        "includes": ["مرشد سياحي", "قارب سنوركلنج", "معدات أساسية"]
    },
}

# ====== بيانات المرشدين لصفحة المعاينة والمرشدين ======
GUIDES = [
    {"id": "g1", "name": "سامي الحربي", "exp": "7 سنوات خبرة", "city": "الرياض", "image": "images/guide1.PNG"},
    {"id": "g2", "name": "خالد الشهري", "exp": "5 سنوات خبرة", "city": "جدة",   "image": "images/guide2.PNG"},
    {"id": "g3", "name": "نورة العتيبي", "exp": "4 سنوات خبرة", "city": "ينبع",  "image": "images/guide3.PNG"},
]

# ---------------------------
# صفحات عامة
# ---------------------------
@app.route("/")
def home():
    featured = [TRIPS["1"], TRIPS["2"], TRIPS["3"]]
    return render_template("home.html", trips=featured, guides=GUIDES, active="home")

@app.route("/trips")
def trips():
    return render_template("trips.html", trips=list(TRIPS.values()), active="trips")

@app.route("/trips/<trip_id>")
def trip_details(trip_id):
    trip = TRIPS.get(str(trip_id))
    if not trip:
        abort(404)
    paid_booking_id = session.get("paid_booking_id")
    return render_template(
        "trip_details.html",
        trip=trip,
        paid_booking_id=paid_booking_id,
        active="trips"
    )

@app.route("/guides")
def guides():
    return render_template("guides.html", guides=GUIDES, active="guides")

# ---------------------------
# الحجز والدفع
# ---------------------------
@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        trip_id = request.form.get("trip_id", "").strip()

        if not (name and email and phone and trip_id and trip_id in TRIPS):
            flash("الرجاء تعبئة جميع الحقول واختيار رحلة صحيحة.", "danger")
            return redirect(url_for("booking"))

        booking_id = str(uuid.uuid4())[:8]
        session["pending_booking"] = {
            "booking_id": booking_id,
            "name": name,
            "email": email,
            "phone": phone,
            "trip_id": trip_id,
        }
        flash("تم إنشاء طلب الحجز. برجاء إتمام الدفع لتأكيده.", "success")
        return redirect(url_for("payment"))

    return render_template("booking.html", trips=list(TRIPS.values()), active="booking")

@app.route("/payment", methods=["GET", "POST"])
def payment():
    data = session.get("pending_booking")
    if not data:
        flash("لا توجد عملية حجز معلّقة.", "danger")
        return redirect(url_for("booking"))

    trip = TRIPS.get(data["trip_id"])
    if request.method == "POST":
        # محاكاة نجاح الدفع
        session["paid_booking_id"] = data["booking_id"]
        flash("تم الدفع بنجاح! يمكنك الآن الاطلاع على بيانات التواصل.", "success")
        return redirect(url_for("thank_you"))

    return render_template("payment.html", booking=data, trip=trip, active="payment")

@app.route("/thank-you")
def thank_you():
    paid = session.get("paid_booking_id")
    return render_template("thank_you.html", paid_booking_id=paid)

# ---------------------------
# ملفات ثابتة مطلوبة
# ---------------------------
@app.route("/service-worker.js")
def service_worker():
    return send_from_directory("static", "service-worker.js", mimetype="application/javascript")

@app.route("/manifest.webmanifest")
def manifest():
    return send_from_directory("static", "manifest.webmanifest", mimetype="application/manifest+json")

@app.route("/robots.txt")
def robots():
    return send_from_directory("static", "robots.txt")

# ---------------------------
# نقطة التشغيل (محليًا)
# ---------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)