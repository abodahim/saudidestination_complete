from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

# ✅ تمرير السنة بشكل تلقائي لكل القوالب
@app.context_processor
def inject_current_year():
    return {"current_year": datetime.now().year}

# ✅ الصفحة الرئيسية
@app.route('/')
def home():
    return render_template("home.html")

# ✅ صفحة الرحلات
@app.route('/trips')
def trips():
    return render_template("trips.html")

# ✅ صفحة تفاصيل الرحلة (اسمها ثابت كما اتفقنا: trip_detail.html)
@app.route('/trip/<slug>')
def trip_detail(slug):
    # بيانات تجريبية
    trip = {
        "title": "رحلة الرياض",
        "city": "الرياض",
        "images": ["riyadh_1.JPG", "riyadh_2.JPG"],
        "summary": "رحلة رائعة في مدينة الرياض تشمل زيارة أهم المعالم.",
        "price_per_day": 500,
        "days_default": 3,
        "slug": slug
    }
    return render_template("trip_detail.html", trip=trip)

# ✅ صفحة المرشدين
@app.route('/guides')
def guides_page():
    return render_template("guides.html")

# ✅ صفحة تواصل
@app.route('/contact')
def contact():
    return render_template("contact.html")

# ✅ صفحة خطأ مخصصة
@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="حدث خطأ داخلي في الخادم"), 500

if __name__ == "__main__":
    app.run(debug=True)