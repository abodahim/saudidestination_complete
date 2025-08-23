import os
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, send_from_directory
)

app = Flask(__name__, static_url_path="/static")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret")
CURRENCY = "ر.س"

# ---------------------------
# البيانات (رحلات + مرشدين)
# ---------------------------
TRIPS = [
    {
        "id": 1,
        "title": "رحلة جدة",
        "city": "جدة",
        "days": 1,
        "price": 299,
        "image": "images/jeddah_1.JPG",
        "summary": "استكشف كورنيش جدة ومعالمها الحديثة."
    },
    {
        "id": 2,
        "title": "رحلة الرياض",
        "city": "الرياض",
        "days": 1,
        "price": 349,
        "image": "images/riyadh_1.JPG",
        "summary": "زيارة الدرعية والمعالم التراثية في العاصمة."
    },
    {
        "id": 3,
        "title": "رحلة ينبع",
        "city": "ينبع",
        "days": 1,
        "price": 399,
        "image": "images/yanbu_1.JPG",
        "summary": "تمتع بالشواطئ والأنشطة البحرية."
    },
]

GUIDES = [
    {"name": "سامي الحربي",  "city": "الرياض", "years": 7, "image": "images/guide1.PNG"},
    {"name": "عبدالله المطيري","city": "جدة",   "years": 5, "image": "images/guide2.PNG"},
    {"name": "أحمد القحطاني", "city": "ينبع",  "years": 6, "image": "images/guide3.PNG"},
]

# ---------------------------
# صفحات عامة
# ---------------------------
@app.route("/")
def home():
    return render_template("home.html",
                           trips=TRIPS,
                           guides=GUIDES,
                           currency=CURRENCY,
                           active="home")

@app.route("/trips")
def trips():
    return render_template("trips.html",
                           trips=TRIPS, currency=CURRENCY, active="trips")

@app.route("/trips/<int:trip_id>")
def trip_details(trip_id: int):
    trip = next((t for t in TRIPS if t["id"] == trip_id), None)
    if not trip:
        return redirect(url_for("trips"))
    return render_template("trip_details.html",
                           trip=trip, currency=CURRENCY, active="trips")

@app.route("/guides")
def guides():
    return render_template("guides.html", guides=GUIDES, active="guides")

# ---------------------------
# الحجز والدفع (تحسين النموذج)
# ---------------------------
@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        name  = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        trip_id = request.form.get("trip_id", "").strip()

        if not name or not email or not phone or not trip_id:
            flash("الرجاء تعبئة جميع الحقول.", "danger")
            return redirect(url_for("booking"))

        # تحقق بسيط
        if "@" not in email or not phone.isdigit() or not phone.startswith("05"):
            flash("تحقق من البريد ورقم الجوال (يبدأ بـ 05).", "danger")
            return redirect(url_for("booking"))

        trip = next((t for t in TRIPS if str(t["id"]) == trip_id), None)
        if not trip:
            flash("الرحلة غير موجودة.", "danger")
            return redirect(url_for("booking"))

        # هنا مكان إنشاء طلب دفع/فاتورة إن رغبت
        flash("تم إرسال طلب الحجز بنجاح. ستظهر بيانات التواصل بعد إتمام الدفع.", "success")
        return redirect(url_for("thank_you", trip_id=trip_id))

    return render_template("booking.html", trips=TRIPS, currency=CURRENCY, active="book")

@app.route("/thank-you")
def thank_you():
    # افترضنا نجاح الدفع لعرض بيانات التواصل (يمكن ربطه ببوابة دفع لاحقاً)
    trip_id = request.args.get("trip_id", type=int)
    trip = next((t for t in TRIPS if t["id"] == trip_id), None)
    return render_template("thank_you.html", trip=trip, active=None)

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
# تشغيل محلي
# ---------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)