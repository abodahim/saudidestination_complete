from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
from fpdf import FPDF
import openpyxl
from openpyxl.styles import Font

app = Flask(__name__)

# الصفحة الرئيسية
@app.route('/')
def home():
    return render_template('index.html')

# صفحة الحجز
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        trip = request.form['trip']
        date = request.form['date']

        conn = sqlite3.connect('bookings.db')
        c = conn.cursor()
        c.execute("INSERT INTO bookings (name, email, trip, date) VALUES (?, ?, ?, ?)",
                  (name, email, trip, date))
        conn.commit()
        conn.close()

        return redirect(url_for('home'))

    return render_template('booking.html')

# لوحة الإدارة: عرض الحجوزات مع فلتر تاريخ
@app.route('/admin/bookings')
def admin_dashboard():
    date_filter = request.args.get('date')
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()

    if date_filter:
        c.execute("SELECT * FROM bookings WHERE date = ?", (date_filter,))
    else:
        c.execute("SELECT * FROM bookings")

    bookings = c.fetchall()
    conn.close()
    return render_template('bookings.html', bookings=bookings)

# حذف حجز
@app.route('/delete/<int:id>')
def delete_booking(id):
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute("DELETE FROM bookings WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

# تصدير إلى PDF
@app.route('/export/pdf')
def export_pdf():
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute("SELECT * FROM bookings")
    bookings = c.fetchall()
    conn.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="قائمة الحجوزات", ln=True, align='C')
    pdf.ln(10)

    for b in bookings:
        pdf.cell(200, 10, txt=f"رقم: {b[0]} - الاسم: {b[1]} - البريد: {b[2]} - الرحلة: {b[3]} - التاريخ: {b[4]}", ln=True)

    pdf.output("bookings.pdf")
    return send_file("bookings.pdf", as_attachment=True)

# تصدير إلى Excel
@app.route('/export/excel')
def export_excel():
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute("SELECT * FROM bookings")
    bookings = c.fetchall()
    conn.close()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "الحجوزات"
    headers = ["رقم", "الاسم", "البريد الإلكتروني", "اسم الرحلة", "تاريخ الحجز"]
    ws.append(headers)

    for b in bookings:
        ws.append(list(b))

    for cell in ws["1:1"]:
        cell.font = Font(bold=True)

    wb.save("bookings.xlsx")
    return send_file("bookings.xlsx", as_attachment=True)
    
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/trip/<int:trip_id>')
def trip_details(trip_id):
    trips = {
        1: {
            'title': 'رحلة إلى شاطئ جدة',
            'description': 'استمتع بجمال البحر الأحمر والأنشطة البحرية الممتعة.',
            'price': 350,
            'date': '2025-07-10',
            'image': 'trip_jeddah.jpg'
        },
        2: {
            'title': 'جولة في الرياض',
            'description': 'استكشاف معالم الرياض الحديثة والتاريخية.',
            'price': 400,
            'date': '2025-07-15',
            'image': 'trip_riyadh.jpg'
        }
        # يمكن إضافة المزيد من الرحلات هنا
    }

    trip = trips.get(trip_id)
    if trip:
        return render_template("trip_details.html", trip=trip)
    else:
        return "الرحلة غير موجودة", 404

if __name__ == '__main__':
    app.run(debug=True)
