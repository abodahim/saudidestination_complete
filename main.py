from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

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
    conn.commit()
    conn.close()

app = Flask(__name__)

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
    return render_template('trips.html')

# صفحة تفاصيل الرحلة
@app.route('/trip/<trip_name>')
def trip_details(trip_name):
    return render_template('trip_details.html', trip_name=trip_name)

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
        c = conn.cursor()
        c.execute("INSERT INTO bookings (name, email, phone, trip, date) VALUES (?, ?, ?, ?, ?)",
                  (name, email, phone, trip, date))
        conn.commit()
        conn.close()

        return redirect(url_for('thank_you'))

    return render_template('booking.html')
    
@app.route('/admin_login')
def admin_login():
    return render_template('admin_login.html')
    
# صفحة الشكر بعد الحجز
@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

# صفحة التقييمات
@app.route('/reviews/<trip>', methods=['GET', 'POST'])
def reviews(trip):
    if request.method == 'POST':
        name = request.form['name']
        rating = request.form['rating']
        comment = request.form['comment']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO reviews (trip, name, rating, comment) VALUES (?, ?, ?, ?)",
                  (trip, name, rating, comment))
        conn.commit()
        conn.close()
        return redirect(url_for('reviews', trip=trip))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT trip, name, rating, comment, created_at FROM reviews WHERE trip = ? ORDER BY id DESC", (trip,))
    all_reviews = c.fetchall()
    conn.close()

    return render_template('reviews.html', trip=trip, reviews=all_reviews)

if __name__ == '__main__':
    app.run(debug=True)