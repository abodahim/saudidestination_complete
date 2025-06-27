from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

# 🔹 تعريف المسارات الثابتة والصور (مهم للعمل على Render)
app = Flask(__name__, static_folder='static', template_folder='templates')

# 🔹 إنشاء قاعدة البيانات تلقائيًا إذا لم تكن موجودة
if not os.path.exists('database.db'):
    conn = sqlite3.connect('database.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            trip TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# 🔹 الصفحة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# 🔹 صفحة "عن الموقع"
@app.route('/about')
def about():
    return render_template('about.html')

# 🔹 صفحة الرحلات
@app.route('/trips')
def trips():
    return render_template('trips.html')

# 🔹 صفحة تفاصيل الرحلة
@app.route('/trip/<trip_name>')
def trip_details(trip_name):
    return render_template('trip_details.html', trip_name=trip_name)

# 🔹 صفحة الحجز
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        trip = request.form['trip']
        date = request.form['date']

        # 🔸 تخزين بيانات الحجز في قاعدة البيانات
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO bookings (name, email, trip, date) VALUES (?, ?, ?, ?)",
                  (name, email, trip, date))
        conn.commit()
        conn.close()

        return redirect(url_for('thank_you'))

    return render_template('booking.html')

# 🔹 صفحة الشكر بعد الحجز
@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

# 🔹 تشغيل التطبيق في الوضع المحلي
if __name__ == '__main__':
    app.run(debug=True)