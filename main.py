import os
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, send_from_directory, jsonify
)

app = Flask(__name__, static_url_path="/static")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret")

# ---------------------------
# صفحات عامة
# ---------------------------
@app.route("/")
def home():
    return render_template("home.html", active="home")

@app.route("/trips")
def trips():
    # إن كانت لديك صفحة رحلات مستقلة
    return render_template("trips.html", active="trips")

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
        # مثال بسيط لمعالجة الرسالة
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        # TODO: احفظ/أرسل الرسالة كما تريد
        flash("تم استلام رسالتك بنجاح، وسنعاود التواصل قريبًا.", "success")
        return redirect(url_for("thank_you"))
    return render_template("contact.html", active="contact")

# ---------------------------
# الحجز والدفع
# ---------------------------
@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        # التحقق السريع
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        trip_name = request.form.get("trip_name", "").strip()

        if not name or not email or not phone or not trip_name:
            flash("الرجاء تعبئة جميع الحقول المطلوبة.", "danger")
            return redirect(url_for("book"))

        # TODO: خزّن الحجز – أرسل بريدًا – أنشئ فاتورة … إلخ
        flash("تم إرسال طلب الحجز بنجاح.", "success")
        return redirect(url_for("thank_you"))
    return render_template("booking.html", active="book")

@app.route("/payment", methods=["GET", "POST"])
def payment():
    # صفحة دفع تجريبية/توضيحية
    if request.method == "POST":
        flash("تم استلام عملية الدفع بنجاح.", "success")
        return redirect(url_for("thank_you"))
    return render_template("payment.html", active="payment")

@app.route("/invoice/<string:booking_id>")
def invoice(booking_id):
    # نموذج بسيط لعرض فاتورة
    return render_template("invoice.html", booking_id=booking_id, active=None)

@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html", active=None)

# ---------------------------
# الدخول والإدارة (شكل مبدئي)
# ---------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # تحقق بسيط – بدّلها لاحقًا بنظام حقيقي
        if request.form.get("username") == "admin" and request.form.get("password") == "admin":
            flash("تم تسجيل الدخول.", "success")
            return redirect(url_for("admin_dashboard"))
        flash("بيانات الدخول غير صحيحة.", "danger")
    return render_template("login.html", active=None)

@app.route("/admin")
def admin_dashboard():
    # لوحة إدارية مبدئية
    return render_template("admin_dashboard.html", active=None)

# ---------------------------
# ملفات ثابتة مطلوبة لتجنّب أخطاء 404 في السجلات
# ---------------------------
@app.route("/service-worker.js")
def service_worker():
    # تأكد من وجود هذا الملف داخل static/ حتى لو فارغ
    return send_from_directory("static", "service-worker.js", mimetype="application/javascript")

@app.route("/manifest.webmanifest")
def manifest():
    return send_from_directory("static", "manifest.webmanifest", mimetype="application/manifest+json")

@app.route("/robots.txt")
def robots():
    return send_from_directory("static", "robots.txt")

@app.route('/booking')
def booking():
    return render_template('booking.html')
# ---------------------------
# نقطة التشغيل
# ---------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
