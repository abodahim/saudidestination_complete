from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # مفتاح الجلسة لتفعيل flash messages

# الصفحة الرئيسية
@app.route('/')
def home():
    return render_template('index.html')

# صفحة الحجز
@app.route('/booking')
def booking():
    return render_template('booking.html')

# استقبال بيانات الحجز
@app.route('/submit_booking', methods=['POST'])
def submit_booking():
    name = request.form['name']
    email = request.form['email']
    date = request.form['date']
    trip_type = request.form['type']

    # بإمكانك هنا تخزين البيانات في قاعدة بيانات أو إرسالها بالبريد
    flash(f'تم استلام الحجز بنجاح للرحلة بتاريخ {date} 🎉', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
