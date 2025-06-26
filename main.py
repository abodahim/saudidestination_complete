from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# إنشاء قاعدة البيانات (إن لم تكن موجودة) عند تشغيل التطبيق
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            trip TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

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
        trip = request.form['trip']
        date = request.form['date']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO bookings (name, email, trip, date) VALUES (?, ?, ?, ?)",
                  (name, email, trip, date))
        conn.commit()
        conn.close()

        return redirect(url_for('thank_you'))

    return render_template('booking.html')

# صفحة الشكر بعد الحجز
@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

# تشغيل التطبيق
if __name__ == '__main__':
    init_db()
    app.run(debug=True)