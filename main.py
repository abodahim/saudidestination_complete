from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

DB_PATH = 'database.db'

def init_db():
    """إنشاء الجداول إذا لم تكن موجودة، وحشو جدول المرشدين ببيانات أولية."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # جدول الحجوزات
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            trip TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    # جدول التقييمات
    c.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip TEXT NOT NULL,
            name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # جدول المرشدين
    c.execute('''
        CREATE TABLE IF NOT EXISTS guides (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            image TEXT NOT NULL,
            bio TEXT NOT NULL,
            experience TEXT NOT NULL
        )
    ''')
    # حشو جدول المرشدين إذا كان فارغًا
    c.execute('SELECT COUNT(*) FROM guides')
    if c.fetchone()[0] == 0:
        guides_seed = [
            (1, 'عبدالله الغامدي', 'guide1.PNG', 'مرشد محترف في جدة', '5 سنوات'),
            (2, 'سارة العتيبي',    'guide2.PNG', 'خبيرة سياحية في الرياض', '3 سنوات'),
            (3, 'فيصل الحربي',     'guide3.PNG', 'دليل محلي في ينبع',        '4 سنوات'),
        ]
        c.executemany('INSERT INTO guides VALUES (?, ?, ?, ?, ?)', guides_seed)
    conn.commit()
    conn.close()

# شغّل التهيئة عند بدء التشغيل
if not os.path.exists(DB_PATH):
    init_db()
else:
    # تأكد من وجود الجداول حتى لو كان الملف موجودًا
    init_db()

# الصفحة الرئيسية
@app.route('/')
def index():
    # جلب أول 3 مرشدين لعرضهم
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM guides ORDER BY id LIMIT 3')
    guides = c.fetchall()
    conn.close()

    # رحلات ثابتة مؤقتًا
    trips = [
        {"id": 1, "title": "رحلة إلى جدة",   "image": "jeddah_1.jpg", "description": "استكشف عروس البحر الأحمر"},
        {"id": 2, "title": "رحلة إلى الرياض", "image": "riyadh_1.jpg", "description": "جولة في العاصمة"},
        {"id": 3, "title": "رحلة إلى ينبع",   "image": "yanbu_1.jpg",  "description": "متعة البحر والطبيعة"},
    ]
    return render_template('index.html', guides=guides, trips=trips)

# صفحة الرحلات
@app.route('/trips')
def trips():
    trips = [
        {"id": 1, "title": "رحلة إلى جدة",   "image": "jeddah_1.jpg", "description": "استكشف عروس البحر الأحمر"},
        {"id": 2, "title": "رحلة إلى الرياض", "image": "riyadh_1.jpg", "description": "جولة في العاصمة"},
        {"id": 3, "title": "رحلة إلى ينبع",   "image": "yanbu_1.jpg",  "description": "متعة البحر والطبيعة"},
    ]
    return render_template('trips.html', trips=trips)

# صفحة عن الموقع
@app.route('/about')
def about():
    return render_template('about.html')

# صفحة الحجز
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name  = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        trip  = request.form['trip']
        date  = request.form['date']

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO bookings (name, email, phone, trip, date) VALUES (?, ?, ?, ?, ?)",
            (name, email, phone, trip, date)
        )
        conn.commit()
        conn.close()

        # مرِّر البيانات إلى صفحة الشكر لعرضها
        return redirect(url_for('thank_you', name=name, trip=trip, date=date))

    return render_template('booking.html')

# صفحة الشكر بعد الحجز
@app.route('/thank_you')
def thank_you():
    name = request.args.get('name')
    trip = request.args.get('trip')
    date = request.args.get('date')
    return render_template('thank_you.html', name=name, trip=trip, date=date)

# صفحة المرشدين (كلهم)
@app.route('/guides')
def guides():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM guides ORDER BY id')
    guides = c.fetchall()
    conn.close()
    return render_template('guides.html', guides=guides)

# صفحة تفاصيل مرشد معين
@app.route('/guide/<int:guide_id>')
def guide_details(guide_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM guides WHERE id = ?', (guide_id,))
    guide = c.fetchone()
    conn.close()

    if guide:
        return render_template('guide_details.html', guide=guide)
    else:
        return "المرشد غير موجود", 404

if __name__ == '__main__':
    app.run(debug=True)