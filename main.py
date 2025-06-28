from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = 'secret123'  # لتأمين الجلسات

# إنشاء قاعدة البيانات إن لم تكن موجودة
if not os.path.exists('database.db'):
    conn = sqlite3.connect('database.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            trip TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# الصفحة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# صفحة الرحلات
@app.route('/trips')
def trips():
    return render_template('trips.html')

# صفحة تفاصيل الرحلة
@app.route('/trip/<trip_name>')
def trip_details(trip_name):
    return render_template('trip_details.html', trip_name=trip_name)

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

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO bookings (name, email, phone, trip, date) VALUES (?, ?, ?, ?, ?)",
                  (name, email, phone, trip, date))
        conn.commit()
        conn.close()

        return redirect(url_for('thank_you'))

    return render_template('booking.html')

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

# صفحة تسجيل دخول المشرف
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        password = request.form['password']
        if password == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            error = 'كلمة المرور غير صحيحة'
    return render_template('login.html', error=error)

# صفحة لوحة التحكم
@app.route('/admin', methods=['GET'])
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    filter_date = request.args.get('filter_date')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if filter_date:
        c.execute("SELECT * FROM bookings WHERE date = ?", (filter_date,))
    else:
        c.execute("SELECT * FROM bookings")
    bookings = c.fetchall()
    conn.close()
    return render_template('admin.html', bookings=bookings)

# حذف حجز
@app.route('/delete/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

# تصدير الحجوزات إلى Excel
@app.route('/export')
def export_bookings():
    conn = sqlite3.connect('database.db')
    df = pd.read_sql_query("SELECT * FROM bookings", conn)
    conn.close()
    file_path = 'static/bookings_export.xlsx'
    df.to_excel(file_path, index=False)
    return redirect(f'/{file_path}')

if __name__ == '__main__':
    app.run(debug=True)