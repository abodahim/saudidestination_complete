from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# ===== دالة إعداد قاعدة البيانات bookings.db =====
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
    print("✅ تم إنشاء قاعدة البيانات bookings.db")

# استدعاء الدالة مرة واحدة عند تشغيل السيرفر
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

        # إدخال بيانات الحجز في قاعدة البيانات
        conn = sqlite3.connect('bookings.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO bookings (name, email, trip) VALUES (?, ?, ?)', (name, email, trip))
        conn.commit()
        conn.close()

        return f"<h3>تم الحجز بنجاح! شكراً {name}</h3><a href='/'>العودة للرئيسية</a>"

    return render_template('booking.html')

# ===== تشغيل التطبيق =====
if __name__ == '__main__':
    app.run(debug=True)
