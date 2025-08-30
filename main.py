# main.py
from flask import Flask, render_template, request, abort
from datetime import datetime

app = Flask(__name__)

# السنة في كل القوالب
@app.context_processor
def inject_current_year():
    return {"current_year": datetime.now().year}

# بيانات الرحلات (صور داخل static/images/)
TRIPS = [
    {
        "slug": "jeddah",
        "title": "رحلة جدة",
        "summary": "استمتع بالكورنيش والمعالم التاريخية في جدة.",
        "images": ["images/jeddah_1.jpg", "images/jeddah_2.jpg"]
    },
    {
        "slug": "riyadh",
        "title": "رحلة الرياض",
        "summary": "اكتشف معالم العاصمة وتجارب حديثة.",
        "images": ["images/riyadh_1.jpg", "images/riyadh_2.jpg"]
    },
    {
        "slug": "yanbu",
        "title": "رحلة ينبع",
        "summary": "شواطئ خلابة وأنشطة بحرية ممتعة.",
        "images": ["images/yanbu_1.jpg", "images/yanbu_2.jpg"]
    },
    {
        "slug": "alula",
        "title": "رحلة العلا",
        "summary": "جبال ساحرة ومواقع تراثية وتجارب صحراوية فريدة.",
        "images": ["images/alula_1.jpg", "images/alula_2.jpg"]
    },
]

def get_trip(slug):
    return next((t for t in TRIPS if t["slug"] == slug), None)

# الصفحات
@app.route("/")
def home():
    # أمثلة مبسطة للواجهة الرئيسية إن كانت تستخدم trips/guides/stats
    stats = {"guides_count": 4, "trips_available": len(TRIPS), "booked": 3}
    guides = []  # املأها إن كنت تعرض مرشدين
    reviews = [] # املأها إن كنت تعرض تقييمات
    return render_template("home.html", trips=TRIPS[:3], guides=guides, stats=stats, reviews=reviews)

@app.route("/trips")
def trips():
    # ✅ يمرّر المتغير المطلوب إلى trips.html
    return render_template("trips.html", trips=TRIPS)

@app.route("/trip/<slug>")
def trip_detail(slug):
    trip = get_trip(slug)
    if not trip:
        abort(404)
    # إن كان لديك قالب trip_detail.html
    return render_template("trip_detail.html", trip=trip)

@app.route("/booking")
def booking():
    trip_slug = request.args.get("trip")
    return render_template("booking.html", trip_slug=trip_slug)

@app.route("/guides")
def guides_page():
    return render_template("guides.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

# صفحات الأخطاء (اختياري لكن مفيد)
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="الصفحة غير موجودة"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="حدث خطأ داخلي في الخادم"), 500

if __name__ == "__main__":
    app.run(debug=True)