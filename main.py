from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# الصفحة الرئيسية
@app.route('/')
def home():
    return render_template('home.html')

# صفحة الحجز
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        trip = request.form.get('trip')
        date = request.form.get('date')
        # هنا ممكن تضيف: إرسال بريد/حفظ قاعدة بيانات
        print(f"حجز جديد: {name}, {email}, {phone}, {trip}, {date}")
        return redirect(url_for('success'))
    return render_template('booking.html')

# صفحة نجاح الحجز
@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True)