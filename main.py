from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    trips = [
        {"id": 1, "title": "رحلة إلى جدة", "image": "jeddah_1.jpg", "description": "استكشف عروس البحر الأحمر"},
        {"id": 2, "title": "رحلة إلى الرياض", "image": "riyadh_1.jpg", "description": "جولة في العاصمة"},
        {"id": 3, "title": "رحلة إلى ينبع", "image": "yanbu_1.jpg", "description": "متعة البحر والطبيعة"}
    ]
    return render_template('index.html', trips=trips)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/trips')
def trips():
    trips = [
        {"id": 1, "title": "رحلة إلى جدة", "image": "jeddah_1.jpg", "description": "استكشف عروس البحر الأحمر"},
        {"id": 2, "title": "رحلة إلى الرياض", "image": "riyadh_1.jpg", "description": "جولة في العاصمة"},
        {"id": 3, "title": "رحلة إلى ينبع", "image": "yanbu_1.jpg", "description": "متعة البحر والطبيعة"}
    ]
    return render_template('trips.html', trips=trips)

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name = request.form['name']
        trip = request.form['trip']
        phone = request.form['phone']
        return render_template('thank_you.html', name=name, trip=trip)
    return render_template('booking.html')

@app.route('/guides')
def guides():
    guides = [
        {"id": 1, "name": "عبدالله الغامدي", "image": "guide1.PNG", "bio": "مرشد محترف في جدة"},
        {"id": 2, "name": "سارة العتيبي", "image": "guide2.PNG", "bio": "خبيرة سياحية في الرياض"},
        {"id": 3, "name": "فيصل الحربي", "image": "guide3.PNG", "bio": "دليل محلي في ينبع"}
    ]
    return render_template('guides.html', guides=guides)

@app.route('/guide/<int:guide_id>')
def guide_details(guide_id):
    guides = {
        1: {"name": "عبدالله الغامدي", "image": "guide1.PNG", "bio": "مرشد محترف في جدة", "experience": "5 سنوات"},
        2: {"name": "سارة العتيبي", "image": "guide2.PNG", "bio": "خبيرة سياحية في الرياض", "experience": "4 سنوات"},
        3: {"name": "فيصل الحربي", "image": "guide3.PNG", "bio": "دليل محلي في ينبع", "experience": "6 سنوات"}
    }
    guide = guides.get(guide_id)
    if guide:
        return render_template('guide_details.html', guide=guide)
    return "المرشد غير موجود", 404

if __name__ == '__main__':
    app.run(debug=True)