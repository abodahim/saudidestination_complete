# -*- coding: utf-8 -*-
from datetime import date
import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-me")

# العملة الافتراضية
CURRENCY = "ر.س"

# بيانات الرحلات (تأكد من وجود الصور داخل static/images)
TRIPS = [
    {
        "id": 1,
        "name": "رحلة جدة",
        "city": "جدة",
        "days": 1,
        "price": 299,
        "image": "images/jeddah.jpg",
        "summary": "استمتع بكورنيش جدة ومعالم البحر الأحمر.",
    },
    {
        "id": 2,
        "name": "رحلة الرياض",
        "city": "الرياض",
        "days": 1,
        "price": 349,
        "image": "images/riyadh.jpg",
        "summary": "معالم العاصمة وأسواقها التراثية.",
    },
    {
        "id": 3,
        "name": "رحلة ينبع",
        "city": "ينبع",
        "days": 1,
        "price": 399,
        "image": "images/yanbu.jpg",
        "summary": "شواطئ وأنشطة بحرية جميلة.",
    },
    {
        "id": 4,
        "name": "رحلة العُلا",
        "city": "العلا",
        "days": 2,
        "price": 649,
        "image": "images/alula.jpg",
        "summary": "مدائن صالح والمغامرات الصحراوية.",
    },
]

def get_trip(trip_id):
    return next((t for t in TRIPS if t["id"] == trip_id), None)

# الصفحة الرئيسية (تُفترض لديك home.html)
@app.route("/", endpoint="home")
def home():
    stats = {
        "booked_count": 3,           # عدد الرحلات المحجوزة (إحصائية ظاهرية)
        "packages_count": len(TRIPS),
        "guides_count": 4,
    }
    return render_template(
        "home.html",
        trips=TRIPS,
        currency=CURRENCY,
        stats=stats,
        active="home"
    )

# صفحة الرحلات (تم توحيد اسم الـ endpoint = trips)
@app.route("/trips", endpoint="trips")
def trips():
    return render_template(
        "trips.html",
        trips=TRIPS,
        currency=CURRENCY,
        active="trips"
    )

# تفاصيل الرحلة (اختياري إن كان لديك قالب trip_details.html)
@app.route("/trips/<int:trip_id>", endpoint="trip_details")
def trip_details(trip_id):
    trip = get_trip(trip_id)
    if not trip:
        return redirect(url_for("trips"))
    return render_template(
        "trip_details.html",
        trip=trip,
        currency=CURRENCY,
        active="trips"
    )

# صفحة الحجز (GET تعرض النموذج / POST يرسل الطلب ويُظهر رسالة نجاح داخل نفس القالب)
@app.route("/book", methods=["GET", "POST"], endpoint="book")
def book():
    selected_id = request.args.get("trip_id", type=int) or request.form.get("trip_id", type=int)
    selected_trip = get_trip(selected_id) if selected_id else None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        days = max(1, min(7, request.form.get("days", type=int) or 1))
        trip = selected_trip

        errors = []
        if not name: errors.append("الاسم مطلوب.")
        if not email: errors.append("البريد الإلكتروني مطلوب.")
        if not phone: errors.append("رقم الجوال مطلوب.")
        if not trip: errors.append("الرجاء اختيار الرحلة.")

        if errors:
            for e in errors:
                flash(e, "danger")
            # إعادة العرض مع القيم الحالية
            return render_template(
                "booking.html",
                trips=TRIPS,
                currency=CURRENCY,
                today=date.today().isoformat(),
                selected_trip_id=selected_id,
                submitted=False,
                active="book"
            )

        total = (trip["price"] if trip else 0) * days
        flash("تم إرسال طلب الحجز بنجاح.", "success")

        return render_template(
            "booking.html",
            trips=TRIPS,
            currency=CURRENCY,
            today=date.today().isoformat(),
            selected_trip_id=trip["id"] if trip else None,
            submitted=True,
            submit_payload={
                "name": name,
                "email": email,
                "phone": phone,
                "trip": trip,
                "days": days,
                "total": total,
            },
            active="book"
        )

    # GET
    return render_template(
        "booking.html",
        trips=TRIPS,
        currency=CURRENCY,
        today=date.today().isoformat(),
        selected_trip_id=selected_trip["id"] if selected_trip else None,
        submitted=False,
        active="book"
    )

# صفحة سياسة الإلغاء (اختياري إن وُجد القالب)
@app.route("/cancellation", endpoint="cancellation")
def cancellation():
    return render_template("cancellation.html", active="cancellation")

# صفحة الأسئلة الشائعة (اختياري)
@app.route("/faq", endpoint="faq")
def faq():
    return render_template("faq.html", active="faq")


if __name__ == "__main__":
    # Render يحدد المنفذ عبر PORT؛ محليًا استخدم 5000
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)