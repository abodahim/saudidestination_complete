from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import datetime

app = Flask(__name__)

# نموذج بيانات الرحلات (يمكنك لاحقًا ربطها بقاعدة بيانات)
trips = [
    {"id": 1, "title": "رحلة جدة", "image": "jeddah_1.jpg", "description": "جولة سياحية في جدة"},
    {"id": 2, "title": "رحلة الرياض", "image": "riyadh_1.jpg", "description": "استكشاف معالم الرياض"},
    {"id": 3, "title": "رحلة ينبع", "image": "yanbu_1.jpg", "description": "رحلة بحرية في ينبع"}
]

@app.route('/')
def index():
    return render_template('index.html', trips=trips)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        trip = request.form['trip']
        date = request.form['date']
        
        # حفظ الحجز في قاعدة البيانات
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO bookings (name, email, phone, trip, date) VALUES (?, ?, ?, ?, ?)",
                  (name, email, phone, trip, date))
        conn.commit()
        conn.close()
        
        return render_template('thank.html', name=name, email=email, phone=phone, trip=trip, date=date)
    
    return render_template('booking.html', trips=trips)

@app.route('/thank')
def thank():
    return render_template('thank.html')

@app.route('/trips')
def trips_page():
    return render_template('trips.html', trips=trips)

@app.route('/guides')
def guides():
    return render_template('guides.html')

@app.route('/guide/<int:guide_id>')
def guide_details(guide_id):
    return render_template('guide_details.html', guide_id=guide_id)

@app.route('/trip/<int:trip_id>')
def trip_details(trip_id):
    trip = next((t for t in trips if t["id"] == trip_id), None)
    if trip:
        return render_template('trip_details.html', trip=trip)
    else:
        return "الرحلة غير موجودة", 404

@app.route('/review/<int:trip_id>', methods=['GET', 'POST'])
def review(trip_id):
    if request.method == 'POST':
        reviewer = request.form['reviewer']
        comment = request.form['comment']
        rating = request.form['rating']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO reviews (trip_id, reviewer, comment, rating) VALUES (?, ?, ?, ?)",
                  (trip_id, reviewer, comment, rating))
        conn.commit()
        conn.close()

        return redirect(url_for('trip_details', trip_id=trip_id))
    
    return render_template('review.html', trip_id=trip_id)

@app.route('/reviews/<int:trip_id>')
def reviews(trip_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT reviewer, comment, rating FROM reviews WHERE trip_id = ?", (trip_id,))
    reviews = c.fetchall()
    conn.close()
    return render_template('reviews.html', reviews=reviews, trip_id=trip_id)

if __name__ == '__main__':
    app.run(debug=True)
