from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# إنشاء قاعدة بيانات trips.db وجدول الرحلات إذا لم تكن موجودة
if not os.path.exists('trips.db'):
    conn = sqlite3.connect('trips.db')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS trips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        image TEXT
    )
    ''')
    trips = [
        ('جدة', 'رحلة إلى مدينة جدة تشمل زيارة كورنيش جدة وواجهة البلد التاريخية.', 'jeddah_1.JPG'),
        ('الرياض', 'استمتع بجولة سياحية في الرياض تشمل برج المملكة والمتحف الوطني.', 'riyadh_1.JPG'),
        ('ينبع', 'جولة بحرية ممتعة في ينبع مع فعاليات شاطئية ومغامرات.', 'yanbu_1.JPG')
    ]
    conn.executemany('INSERT INTO trips (name, description, image) VALUES (?, ?, ?)', trips)
    conn.commit()
    conn.close()

# إنشاء قاعدة بيانات للحجوزات إذا لم تكن موجودة
if not os.path.exists('database.db'):
    conn = sqlite3.connect('database.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            trip TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# دالة جلب جميع الرحلات
def get_all_trips():
    conn = sqlite3.connect('trips.db')
    conn.row_factory = sqlite3.Row
    trips = conn.execute('SELECT * FROM trips').fetchall()
    conn.close()
    return trips

# دالة جلب تفاصيل رحلة حسب id
def get_trip_by_id(trip_id):
    conn = sqlite3.connect('trips.db')
    conn.row_factory = sqlite3.Row
    trip = conn.execute('SELECT * FROM trips WHERE id = ?', (trip_id,)).fetchone()
    conn.close()
    return trip

# الصفحة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# صفحة عن الموقع
@app.route('/about')
def about():
    return render_template('about.html')

# صفحة الرحلات
@app.route('/trips')
def trips():
    all_trips = get_all_trips()
    return render_template('trips.html', trips=all_trips)

# صفحة تفاصيل الرحلة
@app.route('/trip/<int:trip_id>')
def trip_details(trip_id):
    trip = get_trip_by_id(trip_id)
    if trip:
        return render_template('trip_details.html', trip=trip)
    else:
        return "الرحلة غير موجودة", 404

# صفحة الحجز
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        trip = request.form['trip']
        date = request.form['date']

        conn = sqlite3.connect('database.db')
        conn.execute("INSERT INTO bookings (name, email, phone, trip, date) VALUES (?, ?, ?, ?, ?)",
                     (name, email, phone, trip, date))
        conn.commit()
        conn.close()

        return redirect(url_for('thank_you'))

    return render_template('booking.html')

# صفحة الشكر بعد الحجز
@app.route('/thank_you')
def thank_you():
    return "<h2>شكرًا لحجزك معنا!</h2><a href='/'>العودة للرئيسية</a>"

# صفحة لوحة الإدارة (مستقبلاً)
@app.route('/admin')
def admin():
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)
