from flask import Flask, render_template, request, url_for
from datetime import datetime

app = Flask(__name__)

# رابط آمن: إن لم يوجد الراوت يرجع /trips بدل ما يرمي BuildError
def safe_url(endpoint, **values):
    try:
        return url_for(endpoint, **values)
    except Exception:
        return url_for('trips')

@app.context_processor
def inject_globals():
    return {
        "current_year": datetime.now().year,
        "safe_url": safe_url
    }
    
# ========= بيانات تجريبية ثابتة لعرض الصفحات بدون أخطاء =========
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
        "images": ["images/riyadh_1.JPG"],  # تأكد من تطابق الأحرف
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
    {"name": "أبو خالد", "city": "جدة", "years": 6, "photo": "images/guide1.jpg"},
    {"name": "سلمان", "city": "الرياض", "years": 8, "photo": "images/guide2.jpg"},
    {"name": "مشعل", "city": "العلا", "years": 5, "photo": "images/guide3.jpg"},
    {"name": "تركي", "city": "ينبع", "years": 4, "photo": "images/guide4.jpg"},
]

DEMO_REVIEWS = [
    {"name": "أبو خالد", "rating": 5, "text": "تنظيم ممتاز وخدمة رائعة."},
    {"name": "سلمان", "rating": 4, "text": "الرحلة كانت جميلة جدًا."},
    {"name": "موضي", "rating": 5, "text": "التزام واحترافية عالية."},
]

# ========= الصفحات =========

@app.route("/")
def home():
    stats = {"guides_count": len(DEMO_GUIDES), "trips_available": len(DEMO_TRIPS), "booked": 3}
    return render_template(
        "home.html",
        stats=stats,
        trips=DEMO_TRIPS,
        guides=DEMO_GUIDES,
        reviews=DEMO_REVIEWS,
    )

@app.route("/trips")
def trips():
    return render_template("trips.html", trips=DEMO_TRIPS)

# اسم القالب ثابت كما طلبت: trip_detail.html
@app.route("/trip/<slug>")
def trip_detail(slug):
    trip = next((t for t in DEMO_TRIPS if t["slug"] == slug), None)
    if not trip:
        abort(404)
    return render_template("trip_detail.html", trip=trip)

@app.route("/guides")
def guides_page():
    return render_template("guides.html", guides=DEMO_GUIDES)

@app.route("/reviews")
def reviews():
    return render_template("reviews.html", reviews=DEMO_REVIEWS)

@app.route("/booking")
def booking():
    return render_template("booking.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

# صفحة خطأ مخصصة
@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="حدث خطأ داخلي في الخادم"), 500

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="الصفحة غير موجودة"), 404
    
from flask import Flask, render_template, request, url_for
# ...

@app.route('/booking')
def booking():
    # دعم تمرير الرحلة المختارة ?trip=slug (اختياري)
    trip_slug = request.args.get('trip')
    return render_template('booking.html', trip_slug=trip_slug)

if __name__ == "__main__":
    app.run(debug=True)
    
    