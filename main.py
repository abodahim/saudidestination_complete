from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

# تمرير السنة للفوتر
@app.context_processor
def inject_current_year():
    return {"current_year": datetime.now().year}

# ===== بيانات تجريبية بسيطة لتشغيل الواجهة =====
DEMO_STATS = {
    "guides_count": 4,
    "trips_available": 4,
    "booked": 3,
}

DEMO_TRIPS = [
    {
        "title": "رحلة جدة",
        "city": "جدة",
        "images": ["images/jeddah.jpg"],
        "summary": "استمتع بالكورنيش والمعالم التاريخية في جدة.",
        "price_per_day": 450,
        "days_default": 3,
        "slug": "jeddah",
    },
    {
        "title": "رحلة الرياض",
        "city": "الرياض",
        "images": ["riyadh_1.JPG"],  # حافظنا على الاسم كما لديك
        "summary": "اكتشف العاصمة ومعالمها الحديثة.",
        "price_per_day": 500,
        "days_default": 3,
        "slug": "riyadh",
    },
    {
        "title": "رحلة ينبع",
        "city": "ينبع",
        "images": ["images/yanbu.jpg"],
        "summary": "شواطئ خلابة وأنشطة بحرية ممتعة.",
        "price_per_day": 480,
        "days_default": 2,
        "slug": "yanbu",
    },
    {
        "title": "رحلة العلا",
        "city": "العلا",
        "images": ["images/alula.jpg"],
        "summary": "جبال ساحرة ومواقع تراثية وتجارب صحراوية فريدة.",
        "price_per_day": 600,
        "days_default": 2,
        "slug": "alula",
    },
]

DEMO_GUIDES = [
    {"name": "أبو خالد", "city": "جدة", "years": 8, "photo": "images/guide1.jpg"},
    {"name": "سلمان",   "city": "الرياض", "years": 6, "photo": "images/guide2.jpg"},
    {"name": "ندى",     "city": "العلا",  "years": 5, "photo": "images/guide3.jpg"},
    {"name": "خالد",    "city": "ينبع",   "years": 4, "photo": "images/guide4.jpg"},
]

DEMO_REVIEWS = [
    {"name": "أبو خالد", "rating": 5, "text": "تنظيم ممتاز وخدمة رائعة."},
    {"name": "سلمان",   "rating": 4, "text": "التجربة جميلة والمرافقة مفيدة."},
    {"name": "ندى",     "rating": 5, "text": "الأماكن مختارة بعناية."},
]

# ===== الراوتات =====

@app.route("/")
def home():
    # تمرير كل ما يحتاجه home.html
    return render_template(
        "home.html",
        stats=DEMO_STATS,
        trips=DEMO_TRIPS,
        guides=DEMO_GUIDES,
        reviews=DEMO_REVIEWS,
    )

@app.route("/trips")
def trips():
    return render_template("trips.html", trips=DEMO_TRIPS)

# تفاصيل الرحلة (اسم القالب ثابت: trip_detail.html)
@app.route("/trip/<slug>")
def trip_detail(slug):
    trip = next((t for t in DEMO_TRIPS if t["slug"] == slug), None)
    if not trip:
        return render_template("error.html", code=404, message="الرحلة غير موجودة"), 404
    return render_template("trip_detail.html", trip=trip)

# صفحة الحجز التي يستدعيها القالب (مع بارامتر اختياري)
@app.route("/booking")
def booking():
    trip_slug = request.args.get("trip")
    chosen = next((t for t in DEMO_TRIPS if t["slug"] == trip_slug), None) if trip_slug else None
    return render_template("booking.html", trip=chosen)

# صفحة التقييمات التي يستدعيها القالب
@app.route("/reviews")
def reviews():
    return render_template("reviews.html", reviews=DEMO_REVIEWS)

# "مرشدونا" — استخدم اسم endpoint guides ليتطابق مع القوالب
@app.route("/guides")
def guides():
    return render_template("guides.html", guides=DEMO_GUIDES)

@app.route("/contact")
def contact():
    return render_template("contact.html")

# صفحات أخطاء
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="الصفحة غير موجودة"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="حدث خطأ داخلي في الخادم"), 500

if __name__ == "__main__":
    app.run(debug=True)