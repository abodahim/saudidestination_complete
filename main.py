import os
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, send_from_directory, jsonify
)

app = Flask(__name__, static_url_path="/static")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret")
CURRENCY = "ر.س"

# ---------------------------
# بيانات الرحلات والمرشدين
# ---------------------------
TRIPS = [
    {
        "id": 1, "name": "رحلة جدة", "city": "جدة",
        "days_default": 1, "days_min": 1, "days_max": 7,
        "price_per_day": 299,
        "image": "jeddah_1.JPG",
        "summary": "جولة على كورنيش جدة ومعالمها الحديثة."
    },
    {
        "id": 2, "name": "رحلة الرياض", "city": "الرياض",
        "days_default": 1, "days_min": 1, "days_max": 7,
        "price_per_day": 349,
        "image": "riyadh_1.JPG",
        "summary": "تاريخ العاصمة ومعالمها التراثية."
    },
    {
        "id": 3, "name": "رحلة ينبع", "city": "ينبع",
        "days_default": 1, "days_min": 1, "days_max": 7,
        "price_per_day": 399,
        "image": "yanbu_1.JPG",
        "summary": "جمال الشواطئ والأنشطة البحرية."
    },
]

GUIDES = [
    {"name": "سامي الحربي",   "city": "الرياض", "exp": 7, "photo": "guide1.PNG"},
    {"name": "ماجد المطيري",  "city": "جدة",   "exp": 6, "photo": "guide2.PNG"},
    {"name": "عبدالله الشهري","city": "ينبع",  "exp": 5, "photo": "guide3.PNG"},
]

def get_trip(trip_id):
    for t in TRIPS:
        if t["id"] == int(trip_id):
            return t
    return None

# ---------------------------
# صفحات عامة
# ---------------------------
@app.route("/")
def home():
    return render_template(
        "home.html",
        active="home",
        featured_trips=TRIPS,      # نعرضهم كلهم حالياً
        featured_guides=GUIDES     # يظهر في الهوم
    )

@app.route("/trips")
def trips():
    return render_template("trips.html", active="trips", trips=TRIPS)

@app.route("/guides")
def guides():
    return render_template("guides.html", active="guides", guides=GUIDES)

@app.route("/trip/<int:trip_id>")
def trip_details(trip_id):
    trip = get_trip(trip_id)
    if not trip:
        return redirect(url_for("trips"))
    return render_template("trip_details.html", active="trips", trip=trip, currency=CURRENCY)

@app.route("/gallery")
def gallery():
    return render_template("gallery.html", active="gallery")

@app.route("/reviews")
def reviews():
    return render_template("reviews.html", active="reviews")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        flash("تم استلام رسالتك بنجاح، وسنعاود التواصل قريبًا.", "success")
        return redirect(url_for("thank_you"))
    return render_template("contact.html", active="contact")

# ---------------------------
# الحجز والدفع
# ---------------------------
@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        name   = request.form.get("name", "").strip()
        email  = request.form.get("email", "").strip()
        phone  = request.form.get("phone", "").strip()
        trip_id= request.form.get("trip_id", "").strip()
        days   = request.form.get("days", "1").strip()

        if not name or not email or not phone or not trip_id:
            flash("الرجاء تعبئة جميع الحقول المطلوبة.", "danger")
            return redirect(url_for("book"))

        trip = get_trip(trip_id)
        if not trip:
            flash("الرحلة غير موجودة.", "danger")
            return redirect(url_for("book"))

        try:
            days = max(trip["days_min"], min(int(days), trip["days_max"]))
        except ValueError:
            days = trip["days_default"]

        total = days * trip["price_per_day"]
        # هنا تحفظ الحجز بقاعدتك أو ترسله لبريدك...
        flash("تم إرسال طلب الحجز بنجاح.", "success")
        return redirect(url_for("thank_you"))

    # GET
    preselect_id = request.args.get("trip_id", type=int) or TRIPS[0]["id"]
    return render_template("booking.html", active="book", trips=TRIPS, preselect_id=preselect_id, currency=CURRENCY)

@app.route("/api/trip/<int:trip_id>")
def api_trip(trip_id):
    trip = get_trip(trip_id)
    if not trip:
        return jsonify({"ok": False}), 404
    return jsonify({
        "ok": True,
        "id": trip["id"],
        "price_per_day": trip["price_per_day"],
        "days_default": trip["days_default"],
        "days_min": trip["days_min"],
        "days_max": trip["days_max"],
        "name": trip["name"]
    })

@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html", active=None)

# ---------------------------
# ملفات ثابتة (PWA وغيره)
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
# نقطة التشغيل
# ---------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)