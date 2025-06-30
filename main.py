from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# إنشاء قاعدة البيانات تلقائيًا إذا لم تكن موجودة
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            trip TEXT,
            date TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            trip TEXT,
            rating INTEGER,
            comment TEXT,
            date TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS guides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            image TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            image TEXT
        )
    ''')

    conn.commit()
    conn.close()

# استدعاء إنشاء القاعدة
if not os.path.exists('database.db'):
    init_db()

# الصفحة الرئيسية
@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM trips LIMIT 3')
    trips = c.fetchall()
    c.execute('SELECT * FROM guides LIMIT 3')
    guides = c.fetchall()
    conn.close()
    return render_template('index.html', trips=trips, guides=guides)

# صفحة الحجز
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT title FROM trips')
    trips = c.fetchall()
    conn.close()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        trip = request.form['trip']
        date = request.form['date']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO bookings (name, email, phone, trip, date) VALUES (?, ?, ?, ?, ?)',
                  (name, email, phone, trip, date))
        conn.commit()
        conn.close()

        return render_template('thank.html', name=name, email=email, phone=phone, trip=trip, date=date)

    return render_template('booking.html', trips=trips)

# صفحة المرشدين
@app.route('/guides')
def guides():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM guides')
    guides = c.fetchall()
    conn.close()
    return render_template('guides.html', guides=guides)

# صفحة تفاصيل مرشد
@app.route('/guide/<int:guide_id>')
def guide_details(guide_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM guides WHERE id = ?', (guide_id,))
    guide = c.fetchone()
    conn.close()
    return render_template('guide_details.html', guide=guide)

# صفحة عرض الرحلات
@app.route('/trips')
def trips():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM trips')
    trips = c.fetchall()
    conn.close()
    return render_template('trips.html', trips=trips)

# صفحة تفاصيل الرحلة
@app.route('/trip/<int:trip_id>')
def trip_details(trip_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM trips WHERE id = ?', (trip_id,))
    trip = c.fetchone()

    c.execute('SELECT * FROM reviews WHERE trip = ?', (trip[1],))
    reviews = c.fetchall()
    conn.close()

    return render_template('trip_details.html', trip=trip, reviews=reviews)

# صفحة إضافة تقييم
@app.route('/review/<int:trip_id>', methods=['POST'])
def add_review(trip_id):
    name = request.form['name']
    rating = request.form['rating']
    comment = request.form['comment']
    date = datetime.now().strftime('%Y-%m-%d %H:%M')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # احصل على اسم الرحلة
    c.execute('SELECT title FROM trips WHERE id = ?', (trip_id,))
    trip = c.fetchone()

    if trip:
        trip_title = trip[0]
        c.execute('INSERT INTO reviews (name, trip, rating, comment, date) VALUES (?, ?, ?, ?, ?)',
                  (name, trip_title, rating, comment, date))
        conn.commit()

    conn.close()
    return redirect(url_for('trip_details', trip_id=trip_id))

# تشغيل السيرفر
if __name__ == '__main__':
    app.run(debug=True)
