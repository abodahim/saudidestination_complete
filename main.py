from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'database.db'

# إنشاء قاعدة البيانات إذا لم تكن موجودة
def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS bookings
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT, email TEXT, phone TEXT, trip TEXT, date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS reviews
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     trip_id INTEGER, reviewer TEXT, rating INTEGER, comment TEXT)''')
        conn.commit()
        conn.close()

init_db()

# الصفحة الرئيسية
@app.route('/')
def index():
    trips = [
        {"id": 1, "title": "رحلة إلى جدة", "image": "jeddah_1.jpg", "description": "استكشف عروس البحر الأحمر"},
        {"id": 2, "title": "رحلة إلى الرياض", "image": "riyadh_1.jpg", "description": "جولة في العاصمة"},
        {"id": 3, "title": "رحلة إلى ينبع", "image": "yanbu_1.jpg", "description": "متعة البحر والطبيعة"}
    ]
    guides = [
        {"id": 1, "name": "عبدالله الغامدي", "image": "guide1.PNG", "bio": "مرشد محترف في جدة"},
        {"id": 2, "name": "سارة العتيبي", "image": "guide2.PNG", "bio": "خبيرة سياحية في الرياض"},
        {"id": 3, "name": "فيصل الحربي", "image": "guide3.PNG", "bio": "دليل محلي في ينبع"}
    ]
    return render_template('index.html', trips=trips, guides=guides)

# صفحة الرحلات
@app.route('/trips')
def trips():
    trips = [
        {"id": 1, "title": "رحلة إلى جدة", "image": "jeddah_1.jpg", "description": "استكشف عروس البحر الأحمر"},
        {"id": 2, "title": "رحلة إلى الرياض", "image": "riyadh_1.jpg", "description": "جولة في العاصمة"},
        {"id": 3, "title": "رحلة إلى ينبع", "image": "yanbu_1.jpg", "description": "متعة البحر والطبيعة"}
    ]
    return render_template('trips.html', trips=trips)

# تفاصيل رحلة
@app.route('/trip/<int:trip_id>')
def trip_details(trip_id):
    trips = {
        1: {"title": "رحلة إلى جدة", "image": "jeddah_1.jpg", "description": "استكشف عروس البحر الأحمر"},
        2: {"title": "رحلة إلى الرياض", "image": "riyadh_1.jpg", "description": "جولة في العاصمة"},
        3: {"title": "رحلة إلى ينبع", "image": "yanbu_1.jpg", "description": "متعة البحر والطبيعة"}
    }
    trip = trips.get(trip_id)
    if not trip:
        return "الرحلة غير موجودة", 404

    # جلب التقييمات من قاعدة البيانات
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT reviewer, rating, comment FROM reviews WHERE trip_id=?", (trip_id,))
    reviews = c.fetchall()
    conn.close()

    return render_template('trip_details.html', trip=trip, trip_id=trip_id, reviews=reviews)

# حفظ التقييم
@app.route('/submit_review/<int:trip_id>', methods=['POST'])
def submit_review(trip_id):
    reviewer = request.form['reviewer']
    rating = int(request.form['rating'])
    comment = request.form['comment']

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO reviews (trip_id, reviewer, rating, comment) VALUES (?, ?, ?, ?)",
              (trip_id, reviewer, rating, comment))
    conn.commit()
    conn.close()

    return redirect(url_for('trip_details', trip_id=trip_id))

# صفحة المرشدين
@app.route('/guides')
def guides():
    guides = [
        {"id": 1, "name": "عبدالله الغامدي", "image": "guide1.PNG", "bio": "مرشد محترف في جدة"},
        {"id": 2, "name": "سارة العتيبي", "image": "guide2.PNG", "bio": "خبيرة سياحية في الرياض"},
        {"id": 3, "name": "فيصل الحربي", "image": "guide3.PNG", "bio": "دليل محلي في ينبع"}
    ]
    return render_template('guides.html', guides=guides)

# صفحة تفاصيل مرشد
@app.route('/guide/<int:guide_id>')
def guide_details(guide_id):
    guides = {
        1: {"name": "عبدالله الغامدي", "image": "guide1.PNG", "bio": "مرشد محترف في جدة", "experience": "5 سنوات"},
        2: {"name": "سارة العتيبي", "image": "guide2.PNG", "bio": "خبيرة سياحية في الرياض", "experience": "7 سنوات"},
        3: {"name": "فيصل الحربي", "image": "guide3.PNG", "bio": "دليل محلي في ينبع", "experience": "6 سنوات"}
    }
    guide = guides.get(guide_id)
    if not guide:
        return "المرشد غير موجود", 404
    return render_template('guide_details.html', guide=guide)

# صفحة عن الموقع
@app.route('/about')
def about():
    return render_template('about.html')

# نموذج الحجز
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        trip = request.form['trip']
        date = request.form['date']

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO bookings (name, email, phone, trip, date) VALUES (?, ?, ?, ?, ?)",
                  (name, email, phone, trip, date))
        conn.commit()
        conn.close()

        return render_template('thank_you.html', name=name, trip=trip, date=date)
    return render_template('booking.html')

# صفحة شكر بعد الحجز
@app.route('/thankyou')
def thank_you():
    return render_template('thank_you.html')

if __name__ == '__main__':
    app.run(debug=True)