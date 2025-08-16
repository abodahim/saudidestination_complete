from flask import Flask, render_template, request, redirect, url_for, flash
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_key")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        name  = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        trip  = request.form.get("trip", "").strip()

        if not all([name, email, phone, trip]):
            flash("فضلاً أكمل جميع الحقول.", "error")
            return redirect(url_for("booking"))

        flash("تم استلام طلبك بنجاح!", "success")
        return redirect(url_for("home"))

    return render_template("booking.html")

@app.route("/success")
def success():
    return render_template("success.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
