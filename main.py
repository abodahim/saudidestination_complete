import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory

app = Flask(
    __name__,
    static_url_path="/static",
    static_folder="static",
    template_folder="templates",
)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret")

# ===========================
# الصفحات العامة
# ===========================
@app.route("/")
def home():
    return render_template("home.html", active="home")

@app.route("/trips")
def trips():
    return render_template("trips.html", active="trips")

# تفاصيل الرحلة (يُستخدم من زر "عرض التفاصيل" إن رغبت)
@app.route("/trips/<int:trip_id>")
def trip_details(trip_id):
    return render_template("trip_details.html", trip_id=trip_id, active="trips")

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
        _name = request.form.get("name", "").strip()
        _email = request.form.get("email", "").strip()
        _msg = request.form.get("message", "").strip()
        # TODO: احفظ/أرسل الرسالة
        flash("تم استلام رسالتك بنجاح، وسنعاود التواصل قريبًا.", "success")
        return redirect(url_for("thank_you"))
    return render_template("contact.html", active="contact")

# ===========================
# الحجز والدفع
# ===========================
# ندعم /booking و /book لنفس الدالة لتفادي أي روابط قديمة
@app.route("/booking", methods=["GET", "POST"])
@app.route("/book", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        trip_name = request.form.get("trip_name", "").strip()

        if not all([name, email, phone, trip_name]):
            flash("الرجاء تعبئة جميع الحقول المطلوبة.", "danger")
            return redirect(url_for("booking"))

        # TODO: خزّن الحجز/أرسل بريد/أنشئ فاتورة
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
    # الملف موجود داخل static/service-worker.js
    return send_from_directory("static", "service-worker.js", mimetype="application/javascript")

@app.route("/manifest.webmanifest")
def manifest():
    # اسم الملف غيّرته إلى manifest.webmanifest (صحيح)
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