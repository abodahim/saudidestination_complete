from flask import Flask, render_template, abort

# نصرّح بمجلد static صراحةً (مفيد على Render)
app = Flask(__name__, static_folder="static", static_url_path="/static")

# بيانات تجريبية للرحلات (بدّلها لاحقًا بقاعدة بيانات)
TRIPS = [
    {
        "slug": "jeddah",
        "title": "جدة التاريخية",
        "desc": "جولة في البلد، الأسواق التراثية، وممشى الكورنيش.",
        "duration": "يوم واحد",
        "price": "299 ر.س",
        "tag": "عائلية",
        "image": "jeddah_1.JPG",
    },
    {
        "slug": "riyadh",
        "title": "رياض الحداثة",
        "desc": "معالم معاصرة، بوليفارد، وتجارب مطاعم عالمية.",
        "duration": "يومان",
        "price": "549 ر.س",
        "tag": "شركات",
        "image": "riyadh_1.JPG",
    },
    {
        "slug": "yanbu",
        "title": "بحر ينبع",
        "desc": "أنشطة بحرية وشواطئ خلابة وتجربة غوص.",
        "duration": "3 أيام",
        "price": "799 ر.س",
        "tag": "مدرسية",
        "image": "yanbu_1.JPG",
    },
]

@app.route("/")
def home():
    return render_template("index.html", trips=TRIPS)

@app.route("/about")
def about():
    # مؤقتًا: اعرض نفس الصفحة
    return render_template("index.html", trips=TRIPS)

@app.route("/trips/<slug>")
def trip_details(slug):
    trip = next((t for t in TRIPS if t["slug"] == slug), None)
    if not trip:
        abort(404)
    # مؤقتًا اعرض الرئيسية مع إبراز الرحلة لاحقًا سننشئ قالبًا للتفاصيل
    return render_template("index.html", trips=TRIPS)

@app.route("/booking/<slug>")
def booking(slug):
    # Placeholder — لاحقًا سنبني صفحة حجز
    trip = next((t for t in TRIPS if t["slug"] == slug), None)
    if not trip:
        abort(404)
    return f"الحجز لرحلة: {trip['title']} — قريبًا ✨"

@app.route("/health")
def health():
    return "ok", 200

if __name__ == "__main__":
    # للتجربة محليًا
    app.run(host="0.0.0.0", port=5000, debug=True)