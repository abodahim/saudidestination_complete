import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory

app = Flask(__name__, static_url_path="/static")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret")

# ---------------------------
# الصفحات العامة
# ---------------------------
@app.route("/")
def home():
    return render_template("home.html", active="home")

@app.route("/trips")
def trips():
    return render_template("trips.html", active="trips")

# تفاصيل رحلة (المسار الذي كان مفقوداً)
@app.route("/trips/<int:trip_id>")
def trip_details(trip_id: int):
    demo = {
        "id": trip_id,
        "title": f"رحلة رقم {trip_id}",
        "city": "العُلا",
        "days": 3,
        "price": 899
    }
    return render_template("trip_details.html", trip=demo, active="trips")

@app.route("/guides")
def guides():
    return render_template("guides.html", active="guides")

@app.route("/gallery")
def gallery():
    return render_template("gallery.html", active="gallery")

@app.route("/reviews")
def reviews():
    return render_template("reviews.html", active="reviews")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        flash("تم استلام رسالتك بنجاح، وسنعاود التواصل قريبًا.", "success")
        return redirect(url_for("thank_you"))
    return render_template("contact.html", active="contact")

# ---------------------------
# الحجز والدفع (تم توحيد الاسم على /booking)
# ---------------------------
@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        trip_name = request.form.get("trip_name", "").strip()
        if not all([name, email, phone, trip_name]):
            flash("الرجاء تعبئة جميع الحقول المطلوبة.", "danger")
            return redirect(url_for("booking"))
        flash("تم إرسال طلب الحجز بنجاح.", "success")
        return redirect(url_for("thank_you"))
    return render_template("booking.html", active="booking")

@app.route("/payment", methods=["GET", "POST"])
def payment():
    if request.method == "POST":
        flash("تم استلام عملية الدفع بنجاح.", "success")
        return redirect(url_for("thank_you"))
    return render_template("payment.html", active="payment")

@app.route("/invoice/<string:booking_id>")
def invoice(booking_id):
    return render_template("invoice.html", booking_id=booking_id, active=None)

@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html", active=None)

# ---------------------------
# ملفات ثابتة مطلوبة (من داخل static فقط)
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
# صفحات أخطاء
# ---------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500

# ---------------------------
# تشغيل
# ---------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
