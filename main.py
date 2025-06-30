from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# إنشاء قاعدة البيانات إذا لم تكن موجودة
if not os.path.exists('database.db'):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE guides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            bio TEXT,
            experience TEXT,
            image TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            title TEXT,
            description TEXT,
            image TEXT
        )
    ''')
    conn.commit()
    conn.close()

# قراءة البيانات من قاعدة البيانات
def get_all_guides():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    guides = conn.execute("SELECT * FROM guides").fetchall()
    conn.close()
    return guides

def get_all_trips():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    trips = conn.execute("SELECT * FROM trips").fetchall()
    conn.close()
    return trips

def get_guide_by_id(guide_id):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    guide = conn.execute("SELECT * FROM guides WHERE id = ?", (guide_id,)).fetchone()
    conn.close()
    return guide

@app.route('/')
def index():
    guides = get_all_guides()
    trips = get_all_trips()
    return render_template('index.html', guides=guides, trips=trips)

@app.route('/guides')
def guides():
    all_guides = get_all_guides()
    return render_template('guides.html', guides=all_guides)

@app.route('/guide/<int:guide_id>')
def guide_details(guide_id):
    guide = get_guide_by_id(guide_id)
    if guide:
        return render_template('guide_details.html', guide=guide)
    return "المرشد غير موجود", 404

@app.route('/trip/<trip_name>')
def trip_details(trip_name):
    return render_template('trip_details.html', trip_name=trip_name)

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        # من الممكن إضافة الحفظ في قاعدة البيانات هنا
        return redirect(url_for('thank_you'))
    return render_template('booking.html')

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

if __name__ == '__main__':
    app.run(debug=True)
