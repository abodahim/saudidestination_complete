from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "secret-key"  # غيّرها لقيمة سرية في الإنتاج

# بيانات الرحلات
TRIPS = [
    {
        "id": 1,
        "slug": "jeddah",
        "name": "رحلة جدة",
        "city": "جدة",
        "days": 1,
        "price": 299,
        "images": ["jeddah_1.JPG", "jeddah_2.JPG", "jeddah_3.JPG", "jeddah_4.JPG"],
        "desc": "اكتشف سحر مدينة جدة مع جولة تشمل المعالم التراثية والكورنيش."
    },
    {
        "id": 2,
        "slug": "riyadh",
        "name": "رحلة الرياض",
        "city": "الرياض",
        "days": 1,
        "price": 399,
        "images": ["riyadh_1.JPG", "riyadh_2.JPG", "riyadh_3.JPG", "riyadh_4.JPG"],
        "desc": "جولة مميزة لاستكشاف معالم العاصمة السعودية بين التراث والحداثة."
    },
    {
        "id": 3,
        "slug": "yanbu",
        "name": "رحلة ينبع",
        "city": "ينبع",
        "days": 1,
        "price": 399,
        "images": ["yanbu_1.JPG", "yanbu_2.JPG", "yanbu_3.JPG", "yanbu_4.JPG"],
        "desc": "استمتع بجمال الشواطئ والأنشطة البحرية في مدينة ينبع."
    },
    {
        "id": 4,
        "slug": "ala",
        "name": "رحلة العلا",
        "city": "العلا",
        "days": 1,
        "price": 499,
        "images": ["ala_1.JPG", "ala_2.JPG", "ala_3.JPG", "ala_4.JPG"],
        "desc": "رحلة لاكتشاف العلا التاريخية وجبالها الساحرة ومناظرها الفريدة."
    },
]

# بيانات المرشدين (رجال فقط - بدون تكرار)
GUIDES = [
    {"id": 1, "name": "سامي الحربي", "city": "الرياض", "years": 7, "photo": "guide1.JPG"},
    {"id": 2, "name": "خالد الفيفي", "city": "جدة", "years": 5, "photo": "guide2.JPG"},
    {"id": 3, "name": "عبدالله الشهري", "city": "ينبع", "years": 6, "photo": "guide3.JPG"},
    {"id": 4, "name": "ماجد القحطاني", "city": "العلا", "years": 8, "photo": "guide4.JPG"},
]

# الصفحة الرئيسية
@app.route("/")
def home():
    return render_template("home.html", trips=TRIPS, guides=GUIDES)

# صفحة الرحلات
@app.route("/trips")
def trips():
    return render_template("trips.html", trips=TRIPS)

# تفاصيل الرحلة
@app.route("/trips/<int:trip_id>")
def trip_details(trip_id):
    trip = next((t for t in TRIPS if t["id"] == trip_id), None)
    if not trip:
        flash("الرحلة غير موجودة", "danger")
        return redirect(url_for("trips"))
    return render_template("trip_details.html", trip=trip)

# صفحة المرشدين
@app.route("/guides")
def guides():
    return render_template("guides.html", guides=GUIDES)

# الحجز
@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        trip_id = int(request.form.get("trip_id"))
        days = int(request.form.get("days", 1))
        total = int(request.form.get("total_amount", 0))

        trip = next((t for t in TRIPS if t["id"] == trip_id), None)

        if trip:
            flash(f"تم إرسال طلب الحجز بنجاح. الإجمالي: {total} ر.س", "success")
            return redirect(url_for("book_success"))
        else:
            flash("فشل الحجز: الرحلة غير صحيحة", "danger")
            return redirect(url_for("book"))

    return render_template("booking.html", trips=TRIPS)

# صفحة نجاح الحجز
@app.route("/book/success")
def book_success():
    return render_template("book_success.html")

# تشغيل التطبيق محلياً
if __name__ == "__main__":
    app.run(debug=True)