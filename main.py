from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/booking')
def booking():
    return "<h2>صفحة الحجز قيد التطوير</h2>"

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        # يمكنك هنا إرسال البريد أو حفظ البيانات
        print(f"تم استلام رسالة من {name} ({email}): {message}")
        return "<h2>تم إرسال رسالتك بنجاح! شكرًا لتواصلك معنا.</h2>"
    return render_template('contact.html')

if __name__ == '__main__':
    app.run()