# main.py
import os
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, send_from_directory
)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("APP_SECRET_KEY", "change_this_secret_key")

# =========================
# بيانات تجريبية (عدّل كما يلزم)
# =========================
TRIPS = [
    {
        "slug": "jeddah",
        "title": "رحلة جدة",
        "city": "جدة",
        "days_default": 1,
        "price_per_day": 299,
        "images": [
            "images/jeddah_1.JPG",
            "images/jeddah_2.JPG",
            "images/jeddah_3.JPG",
            "images/jeddah_4.JPG",
        ],
        "summary": "استمتع بسحر الكورنيش والمعالم التاريخية في جدة.",
    },
    {
        "slug": "riyadh",
        "title": "رحلة الرياض",
        "city": "الرياض",
        "days_default": 1,
        "price_per_day": 349,
        "images": [
            "images/riyadh_1.JPG",
            "images/riyadh_2.JPG",
            "images/riyadh_3.JPG",
            "images/riyadh_4.JPG",
        ],
        "summary": "اكتشف معالم العاصمة والتجارب الحديثة في الرياض.",
    },
    {
        "slug": "yanbu",
        "title": "رحلة ينبع",
        "city": "ينبع",
        "days_default": 1,
        "price_per_day": 399,
        "images": [
            "images/yanbu_1.JPG",
            "images/yanbu_2.JPG",
            "images/yanbu_3.JPG",
            "images/yanbu_4.JPG",
        ],
        "summary": "شواطئ خلابة وأنشطة بحرية ممتعة في ينبع.",
    },
    {
        "slug": "alula",
        "title": "رحلة العلا",
        "city": "العلا",
        "days_default": 1,
        "price_per_day": 499,
        "images": [
            "images/ala_1.JPG",
            "images/ala_2.JPG",
            "images/ala_3.JPG",
            "images/ala_4.JPG",
        ],
        "summary": "جبال ساحرة ومواقع تراثية وتجارب صحراوية فريدة.",
    },
]

GUIDES = [
    {"name": "سامي الحربي", "city": "الرياض", "years": 7, "photo": "images/guide1.PNG"},
    {"name": "ماجد المطيري", "city": "جدة",   "years": 5, "photo": "images/guide2.PNG"},
    {"name": "عبدالعزيز الدوسري", "city": "ينبع", "years": 6, "photo": "images/guide3.PNG"},
    {"name": "فهد الشهري", "city": "العلا",  "years": 8, "photo": "images/guide1.PNG"},
]

REVIEWS = [
    {"name": "أبو خالد", "rating": 5, "text": "تنظيم ممتاز وخدمة رائعة.", "trip": "jeddah"},
    {"name": "سلمان",   "rating": 4, "text": "البرنامج ممتع والأسعار مناسبة.", "trip": "riyadh"},
    {"name": "نايف",    "rating": 5, "text": "تجربة لا تُنسى في العلا.", "trip": "alula"},
]

FAQS = [
    {"q": "كيف أحجز رحلة؟", "a": "من صفحة الحجز اختر الرحلة والأيام ثم أكمل البيانات وأرسل الطلب."},
    {"q": "هل يوجد استرجاع؟", "a": "يمكن الإلغاء قبل 48 ساعة واسترداد 80% وفق سياسة الإلغاء."},
    {"q": "هل السعر يشمل الوجبات؟", "a": "تختلف باختلاف الرحلة، التفاصيل مذكورة في صفحة كل رحلة."},
]

BOOKED_COUNT = 3  # إحصائية مبدئية

# =========================
# مساعدات
# =========================
def get_trip(slug: str):
    return next((t for t in TRIPS if t["slug"] == slug), None)

# =========================
# صفحات عامة
# =========================
@app.route("/")
def home():
    stats = {
        "booked": BOOKED_COUNT,
        "trips_available": len(TRIPS),
        "guides_count": len(GUIDES),
    }
    return render_template(
        "home.html",
        stats=stats,
        trips=TRIPS,
        guides=GUIDES[:3],
        reviews=REVIEWS[:3],
    )

@app.route("/trips")
def trips():
    return render_template("trips.html", trips=TRIPS)

@app.route("/trips/<slug>")
def trip_detail(slug):
    trip = get_trip(slug)
    if not trip:
        flash("لم يتم العثور على الرحلة المطلوبة.", "warning")
        return redirect(url_for("trips"))
    return render_template("trip_detail.html", trip=trip)

@app.route("/guides")
def guides():
    return render_template("guides.html", guides=GUIDES)

@app.route("/reviews")
def reviews():
    return render_template("reviews.html", reviews=REVIEWS)

@app.route("/faq")
def faq():
    return render_template("faq.html", faqs=FAQS)

@app.route("/cancellation")
def cancellation():
    return render_template("cancellation.html")

# favicon (اختياري—مطابق لمكانك الحالي static/images/)
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.static_folder, "images"),
        "favicon.png",
        mimetype="image/png",
    )

# =========================
# الحجز
# =========================
@app.route("/booking", methods=["GET", "POST"])
def booking():
    global BOOKED_COUNT

    if request.method == "GET":
        chosen_slug = request.args.get("trip") or (TRIPS[0]["slug"] if TRIPS else "")
        chosen = get_trip(chosen_slug) if chosen_slug else None
        return render_template(
            "booking.html",
            trips=TRIPS,
            chosen=chosen,
            min_days=1,
            max_days=7,
        )

    # POST
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()
    phone = (request.form.get("phone") or "").strip()
    trip_slug = request.form.get("trip")
    days_raw = request.form.get("days") or "1"
    agree = request.form.get("agree")  # "on" إذا تم التأشير

    trip = get_trip(trip_slug) if trip_slug else None
    try:
        days = max(1, min(7, int(days_raw)))
    except ValueError:
        days = 1

    if not (name and email and phone and trip and agree):
        flash("يرجى استكمال جميع الحقول والموافقة على سياسة الإلغاء.", "danger")
        # إعادة عرض النموذج مع اختيار الرحلة السابقة إن وُجدت
        return redirect(url_for("booking", trip=trip_slug or ""))

    total_price = days * trip["price_per_day"]

    # حفظ ملخص الحجز في الجلسة لعرضه في صفحة التأكيد
    session["last_booking"] = {
        "name": name,
        "email": email,
        "phone": phone,
        "trip": {
            "slug": trip["slug"],
            "title": trip["title"],
            "city": trip["city"],
            "price_per_day": trip["price_per_day"],
        },
        "days": days,
        "total_price": total_price,
        "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    }

    BOOKED_COUNT += 1
    return redirect(url_for("book_success"))

@app.route("/book_success")
def book_success():
    data = session.get("last_booking")
    if not data:
        flash("لا يوجد حجز لعرضه.", "warning")
        return redirect(url_for("booking"))
    return render_template("book_success.html", data=data)

# =========================
# صفحات أخطاء ودّية
# =========================
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="الصفحة غير موجودة"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="حدث خطأ داخلي في الخادم"), 500

# =========================
# تشغيل محلي
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)