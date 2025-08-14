from flask import Flask, render_template, abort, send_from_directory

app = Flask(__name__, static_folder="static", static_url_path="/static")

TRIPS = [
    {
        "slug": "jeddah",
        "title": "رحلة جدة",
        "desc": "جولة على شاطئ البحر الأحمر والمعالم التاريخية.",
        "image": "jeddah_1.JPG",
        "price": "299 ر.س",
        "duration": "يوم واحد",
        "category": "عائلية",
    },
    {
        "slug": "riyadh",
        "title": "رحلة الرياض",
        "desc": "زيارة أهم المعالم الثقافية والتراثية في العاصمة.",
        "image": "riyadh_1.JPG",
        "price": "549 ر.س",
        "duration": "يومان",
        "category": "شركات",
    },
    {
        "slug": "yanbu",
        "title": "رحلة ينبع",
        "desc": "استكشاف الجزر والشواطئ الرملية الساحرة.",
        "image": "yanbu_1.JPG",
        "price": "799 ر.س",
        "duration": "3 أيام",
        "category": "مدرسية",
    },
]

@app.route("/")
def home():
    return render_template("index.html", trips=TRIPS)

@app.route("/trip/<slug>")
def trip(slug):
    t = next((x for x in TRIPS if x["slug"] == slug), None)
    if not t:
        abort(404)
    return render_template("trip.html", trip=t)

@app.route("/booking/<slug>")
def booking(slug):
    t = next((x for x in TRIPS if x["slug"] == slug), None)
    if not t:
        abort(404)
    return f"تم اختيار الحجز لرحلة: {t['title']} — (نموذج الحجز قادم)."

# ملفات الفهرسة
@app.route("/robots.txt")
def robots():
    return send_from_directory(".", "robots.txt", mimetype="text/plain")

@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(".", "sitemap.xml", mimetype="application/xml")

@app.route("/health")
def health():
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
