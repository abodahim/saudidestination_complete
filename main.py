from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

# إنشاء تطبيق Flask
app = Flask(__name__)

# إعداد مفتاح سري لحفظ الجلسة (مطلوب لحماية تسجيل الدخول)
app.secret_key = 'mysecretkey'

# كلمة المرور للدخول إلى صفحة الإدارة
ADMIN_PASSWORD = '1234'

# ===== دالة لإنشاء قاعدة البيانات إذا لم تكن موجودة =====
def setup_database():
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            trip TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# تشغيل الدالة عند تشغيل التطبيق لأول مرة
setup_database()

# ===== الصفحة الرئيسية =====
@app.route('/')
def home():
    return render_template('index.html')

# ===== صفحة الحجز =====
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        trip = request.form['trip']

        # حفظ بيانات الحجز في قاعدة البيانات
        conn = sqlite3.connect('bookings.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO bookings (name, email, trip) VALUES (?, ?, ?)', (name, email, trip))
        conn.commit()
        conn.close()

        return f"<h3>✅ تم الحجز بنجاح! شكراً {name}</h3><a href='/'>العودة للرئيسية</a>"

    return render_template('booking.html')

# ===== صفحة تسجيل الدخول للمشرف =====
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        entered_password = request.form['password']
        if entered_password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('show_bookings'))
        else:
            return render_template('admin_login.html', error='❌ كلمة المرور غير صحيحة!')
    return render_template('admin_login.html')

# ===== صفحة عرض الحجوزات (محميّة) =====
@app.route('/admin/bookings')
def show_bookings():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings ORDER BY created_at DESC')
    bookings = cursor.fetchall()
    conn.close()

    return render_template('bookings.html', bookings=bookings)

# ===== تسجيل الخروج =====
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# ===== تشغيل التطبيق محلياً =====
if __name__ == '__main__':
    app.run(debug=True)
