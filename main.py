from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# الصفحة الرئيسية
@app.route('/')
def home():
    trips = [
        {"id": 1, "title": "رحلة إلى جدة", "image": "jeddah_1.jpg", "description": "استكشف عروس البحر الأحمر"},
        {"id": 2, "title": "رحلة إلى الرياض", "image": "riyadh_1.jpg", "description": "جولة في العاصمة"},
        {"id": 3, "title": "رحلة إلى ينبع", "image": "yanbu_1.jpg", "description": "متعة البحر والطبيعة"}
    ]
    return render_template('index.html', trips=trips)

# صفحة الرحلات
@app.route('/trips')
def trips():
    trips = [
        {"id": 1, "title": "رحلة إلى جدة", "image": "jeddah_1.jpg", "description": "استكشف عروس البحر الأحمر"},
        {"id": 2, "title": "رحلة إلى الرياض", "image": "riyadh_1.jpg", "description": "جولة في العاصمة"},
        {"id": 3, "title": "رحلة إلى ينبع", "image": "yanbu_1.jpg", "description": "متعة البحر والطبيعة"}
    ]
    return render_template('trips.html', trips=trips)

# صفحة عن الموقع
@app.route('/about')
def about():
    return render_template('about.html')

# صفحة الحجز
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name = request.form['name']
        trip = request.form['trip']
        phone = request.form['phone']
        return render_template('thank_you.html', name=name, trip=trip)
    return render_template('booking.html')

# المرشدين
@app.route('/guides')
def guides():
    guides = [
        {"id": 1, "name": "عبدالله الغامدي", "image": "guide1.PNG", "bio": "مرشد محترف في جدة", "experience": "5 سنوات"},
        {"id": 2, "name": "سارة العتيبي", "image": "guide2.PNG", "bio": "خبيرة سياحية في الرياض", "experience": "3 سنوات"},
        {"id": 3, "name": "فيصل الحربي", "image": "guide3.PNG", "bio": "دليل محلي في ينبع", "experience": "4 سنوات"}
    ]
    return render_template('guides.html', guides=guides)

# تفاصيل المرشد + تواصل
@app.route('/guide/<int:guide_id>', methods=['GET', 'POST'])
def guide_details(guide_id):
    guides = {
        1: {"name": "عبدالله الغامدي", "image": "guide1.PNG", "bio": "مرشد محترف في جدة", "experience": "5 سنوات"},
        2: {"name": "سارة العتيبي", "image": "guide2.PNG", "bio": "خبيرة سياحية في الرياض", "experience": "3 سنوات"},
        3: {"name": "فيصل الحربي", "image": "guide3.PNG", "bio": "دليل محلي في ينبع", "experience": "4 سنوات"}
    }
    guide = guides.get(guide_id)

    if request.method == 'POST':
        sender = request.form['sender']
        message = request.form['message']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, guide_id INTEGER, sender TEXT, message TEXT)")
        c.execute("INSERT INTO messages (guide_id, sender, message) VALUES (?, ?, ?)", (guide_id, sender, message))
        conn.commit()
        conn.close()
        return render_template('thank_you.html', name=sender, trip=guide['name'])

    if guide:
        return render_template('guide_details.html', guide=guide)
    else:
        return "المرشد غير موجود", 404

# صفحة الإدارة وهمية مؤقتًا
@app.route('/admin_login')
def admin_login():
    return "صفحة تسجيل دخول المشرف تحت الإنشاء"

if __name__ == '__main__':
    app.run(debug=True)