from flask import Flask, render_template, request, redirect, Response
import sqlite3
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

# ========== إعداد قاعدة البيانات ==========
def init_db():
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        city TEXT,
        trip_type TEXT,
        people INTEGER,
        date TEXT,
        notes TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

# ========== بيانات الدخول للإدارة ==========
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '1234'

def check_auth(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def authenticate():
    return Response(
        'الوصول مرفوض: يرجى إدخال اسم المستخدم وكلمة المرور.', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

# ========== الصفحة الرئيسية ==========
@app.route('/')
def home():
    return render_template('index.html')

# ========== صفحة الحجز ==========
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        city = request.form['city']
        trip_type = request.form['trip_type']
        people = request.form['people']
        date = request.form['date']
        notes = request.form['notes']

        # حفظ في قاعدة البيانات
        conn = sqlite3.connect('bookings.db')
        c = conn.cursor()
        c.execute('INSERT INTO bookings (name, email, phone, city, trip_type, people, date, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
                  (name, email, phone, city, trip_type, people, date, notes))
        conn.commit()
        conn.close()

        # إرسال بريد (اختياري - فعّله لاحقًا)
        # send_email(name, email, phone, city, trip_type, people, date, notes)

        return redirect('/')
    return render_template('booking.html')

# ========== صفحة عرض الحجوزات ==========
@app.route('/admin/bookings')
def admin_bookings():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute('SELECT * FROM bookings')
    bookings = c.fetchall()
    conn.close()
    return render_template('admin_bookings.html', bookings=bookings)

# ========== إرسال البريد (غير مفعّل حالياً) ==========
def send_email(name, email, phone, city, trip_type, people, date, notes):
    msg = EmailMessage()
    msg['Subject'] = 'طلب حجز جديد'
    msg['From'] = 'YOUR_EMAIL@gmail.com'
    msg['To'] = 'YOUR_EMAIL@gmail.com'

    body = f"""
    اسم العميل: {name}
    البريد الإلكتروني: {email}
    رقم الجوال: {phone}
    المدينة: {city}
    نوع الرحلة: {trip_type}
    عدد الأشخاص: {people}
    التاريخ: {date}
    ملاحظات إضافية: {notes}
    """

    msg.set_content(body)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('YOUR_EMAIL@gmail.com', 'APP_PASSWORD')
        smtp.send_message(msg)

# ========== تشغيل التطبيق ==========
if __name__ == '__main__':
    app.run(debug=True)
