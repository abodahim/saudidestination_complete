# main.py
from flask import Flask, render_template, request

app = Flask(__name__)

# الصفحة الرئيسية
@app.route('/')
def index():
    trips = [
        {"id": 1, "title": "رحلة إلى جدة",  "image": "jeddah_1.jpg", "description": "استكشف عروس البحر الأحمر"},
        {"id": 2, "title": "رحلة إلى الرياض", "image": "riyadh_1.jpg", "description": "جولة في العاصمة"},
        {"id": 3, "title": "رحلة إلى ينبع",  "image": "yanbu_1.jpg",  "description": "متعة البحر والطبيعة"}
    ]
    return render_template('index.html', trips=trips)

# صفحة الرحلات
@app.route('/trips')
def trips():
    trips = [
        {"id": 1, "title": "رحلة إلى جدة",  "image": "jeddah_1.jpg", "description": "استكشف عروس البحر الأحمر"},
        {"id": 2, "title": "رحلة إلى الرياض", "image": "riyadh_1.jpg", "description": "جولة في العاصمة"},
        {"id": 3, "title": "رحلة إلى ينبع",  "image": "yanbu_1.jpg",  "description": "متعة البحر والطبيعة"}
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
        name  = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        trip  = request.form['trip']
        date  = request.form['date']
        return render_template('thank_you.html',
                               name=name,
                               email=email,
                               phone=phone,
                               trip=trip,
                               date=date)
    return render_template('booking.html')

# صفحة المرشدين
@app.route('/guides')
def guides():
    guides = [
        {"id": 1, "name": "عبدالله الغامدي", "image": "guide1.PNG", "bio": "مرشد محترف في جدة"},
        {"id": 2, "name": "سارة العتيبي",   "image": "guide2.PNG", "bio": "خبيرة سياحية في الرياض"},
        {"id": 3, "name": "فيصل الحربي",    "image": "guide3.PNG", "bio": "دليل محلي في ينبع"}
    ]
    return render_template('guides.html', guides=guides)

# صفحة تفاصيل المرشد
@app.route('/guide/<int:guide_id>')
def guide_details(guide_id):
    all_guides = {
        1: {"name": "عبدالله الغامدي", "image": "guide1.PNG", "bio": "مرشد محترف في جدة"},
        2: {"name": "سارة العتيبي",   "image": "guide2.PNG", "bio": "خبيرة سياحية في الرياض"},
        3: {"name": "فيصل الحربي",    "image": "guide3.PNG", "bio": "دليل محلي في ينبع"}
    }
    guide = all_guides.get(guide_id)
    if not guide:
        return "المرشد غير موجود", 404
    return render_template('guide_details.html', guide=guide)

# صفحة الإدارة (ربطها من القائمة عبر url_for('admin_login'))
@app.route('/admin')
def admin_login():
    return render_template('admin_login.html')

if __name__ == '__main__':
    app.run(debug=True)