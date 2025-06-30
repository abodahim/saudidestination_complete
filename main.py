from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# إنشاء قاعدة البيانات إذا لم تكن موجودة
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
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip TEXT NOT NULL,
            name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS guides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            image TEXT NOT NULL,
            experience TEXT,
            bio TEXT
        )
    ''')
    conn.commit()
    conn.close()

# الصفحة الرئيسية
@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    guides = conn.execute("SELECT * FROM guides").fetchall()
    conn.close()
    return render_template('index.html', guides=guides)

# صفحة عن الموقع
@app.route('/about')
def about():
    return render_template('about.html')

# صفحة الرحلات
@app.route('/trips')
def trips():
    return render_template('trips.html')

# صفحة تفاصيل الرحلة
@app.route('/trip/<trip_name>')
def trip_details(trip_name):
    return render_template('trip_details.html', trip_name=trip_name)

# صفحة المرشدين
@app.route('/guides')
def guides():
    conn = sqlite3.connect('database.db')
    guides = conn.execute("SELECT * FROM guides").fetchall()
    conn.close()
    return render_template('guides.html', guides=guides)

# صفحة تفاصيل المرشد
@app.route('/guide/<int:guide_id>')
def guide_details(guide_id):
    conn = sqlite3.connect('database.db')
    guide = conn.execute("SELECT * FROM guides WHERE id = ?", (guide_id,)).fetchone()
    conn.close()
    return render_template('guide_details.html', guide=guide)

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

        return render_template('thank_you.html', name=name, email=email, phone=phone, trip=trip, date=date)

    return render_template('booking.html')

# صفحة التقييمات
@app.route('/reviews/<trip>', methods=['GET', 'POST'])
def reviews(trip):
    if request.method == 'POST':
        name = request.form['name']
        rating = request.form['rating']
        comment = request.form['comment']

        conn = sqlite3.connect('database.db')
        conn.execute("INSERT INTO reviews (trip, name, rating, comment) VALUES (?, ?, ?, ?)",
                     (trip, name, rating, comment))
        conn.commit()
        conn.close()
        return redirect(url_for('reviews', trip=trip))

    conn = sqlite3.connect('database.db')
    all_reviews = conn.execute("SELECT * FROM reviews WHERE trip = ? ORDER BY id DESC", (trip,)).fetchall()
    conn.close()

    return render_template('reviews.html', trip=trip, reviews=all_reviews)

# صفحة تسجيل دخول المشرف
@app.route('/admin_login')
def admin_login():
    return render_template('admin_login.html')

if __name__ == '__main__':
    app.run(debug=True)
