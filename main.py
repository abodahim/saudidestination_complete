from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# الصفحة الرئيسية
@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM guides")
    guides = c.fetchall()
    c.execute("SELECT * FROM trips")
    trips = c.fetchall()
    conn.close()
    return render_template('index.html', guides=guides, trips=trips)

# صفحة عرض المرشدين
@app.route('/guides')
def guide_list():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM guides")
    guides = c.fetchall()
    conn.close()
    return render_template('guides.html', guides=guides)

# صفحة تفاصيل مرشد
@app.route('/guide/<int:guide_id>')
def guide_details(guide_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM guides WHERE id = ?", (guide_id,))
    guide = c.fetchone()
    conn.close()
    return render_template('guide_details.html', guide=guide)

# صفحة تفاصيل رحلة
@app.route('/trip/<int:trip_id>')
def trip_details(trip_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM trips WHERE id = ?", (trip_id,))
    trip = c.fetchone()
    c.execute("SELECT * FROM reviews WHERE trip_id = ?", (trip_id,))
    reviews = c.fetchall()
    conn.close()
    return render_template('trip_details.html', trip=trip, reviews=reviews)

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
        return render_template('thank.html', name=name, trip=trip, date=date)
    return render_template('booking.html')

# صفحة تقييم رحلة
@app.route('/review/<int:trip_id>', methods=['POST'])
def add_review(trip_id):
    reviewer = request.form['reviewer']
    rating = request.form['rating']
    comment = request.form['comment']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO reviews (trip_id, reviewer, rating, comment) VALUES (?, ?, ?, ?)",
              (trip_id, reviewer, rating, comment))
    conn.commit()
    conn.close()
    return redirect(url_for('trip_details', trip_id=trip_id))

if __name__ == '__main__':
    app.run(debug=True)
