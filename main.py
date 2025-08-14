from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# تحميل ملف .env من مسار Render
load_dotenv('/etc/secrets/.env')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# إعدادات البريد
SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT', 465))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
BOOKING_EMAIL_TO = os.getenv('BOOKING_EMAIL_TO')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book_trip():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    trip = request.form.get('trip')

    # نص الرسالة
    message_body = f"""
    اسم العميل: {name}
    البريد الإلكتروني: {email}
    رقم الجوال: {phone}
    الرحلة: {trip}
    """

    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = BOOKING_EMAIL_TO
        msg['Subject'] = 'حجز رحلة جديد'
        msg.attach(MIMEText(message_body, 'plain'))

        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        return redirect(url_for('home'))
    except Exception as e:
        return f"حدث خطأ أثناء إرسال البريد: {e}"

if __name__ == '__main__':
    app.run(debug=True)