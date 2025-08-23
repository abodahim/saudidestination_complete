import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory

app = Flask(__name__, static_url_path="/static")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret")

# ---------------------------
# بيانات الرحلات (مثال ثابت)
# ---------------------------
TRIPS = {
    1: {"id": 1, "title": "رحلة جدة",   "price": 299, "city": "جدة",   "days": 1, "img": "images/jeddah_1.JPG"},
    2: {"id": 2, "title": "رحلة الرياض","price": 349, "city": "الرياض","days": 1, "img": "images/riyadh_1.JPG"},
    3: {"id": 3, "title": "رحلة ينبع",  "price": 399, "city": "ينبع",  "days": 1, "img": "images/yanbu_1.JPG"},
}

# ---------------------------
# صفحات عامة
# ---------------------------
@app.route("/")
def home():
    return render_template("home.html", trips=list(TRIPS.values()), active="home")

@app.route("/trips")
def trips():
    return render_template("trips.html", trips=list(TRIPS.values()), active="trips")

# تثبيت اسم الـendpoint ليكون 'trip_details'
@app.route("/trips/<int:trip_id>", endpoint="trip_details")
def trip_details(trip_id: int):
    trip = TRIPS.get(trip_id)
    if not trip:
        return render_template("404.html"), 404
    return render_template("trip_details.html", trip=trip, active="trips")

# نوحّد endpoint الحجز باسم 'book' ونجعل /booking يعمل أيضًا
@app.route("/book", methods=["GET", "POST"], endpoint="book")
@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        # تحقق مبسط
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        trip_id = request.form.get("trip_id", type=int)
        if not (name and email and phone and trip_id and trip_id in TRIPS):
            flash("الرجاء تعبئة جميع الحقول واختيار رحلة صحيحة.", "danger")
            return redirect(url_for("book"))
        flash("تم إرسال طلب الحجز بنجاح.", "success")
        return redirect(url_for("thank_you"))
    # دعم تمرير trip_id من الأزرار
    trip_id = request.args.get("trip_id", type=int)
    trip = TRIPS.get(trip_id) if trip_id else None
    return render_template("booking.html", trips=list(TRIPS.values()), trip=trip, active="book")

@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")

# صفحات أخرى اختيارية (إن وُجدت لديك قوالبها)
@app.route("/guides")
def guides():
    return render_template("guides.html", active="guides")

@app.route("/gallery")
def gallery():
    return render_template("gallery.html", active="gallery")

@app.route("/reviews")
def reviews():
    return render_template("reviews.html", active="reviews")

@app.route("/contact")
def contact():
    return render_template("contact.html", active="contact")

# ---------------------------
# ملفات ثابتة (PWA/SEO)
# ---------------------------
@app.route("/service-worker.js")
def service_worker():
    return send_from_directory("static", "service-worker.js", mimetype="application/javascript")

@app.route("/manifest.webmanifest")
def manifest():
    # اسم الملف لديك manifest.webmanifest داخل static/
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