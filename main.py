# استيراد الحزم اللازمة من فلاسـك وSQLite
from flask import Flask, render_template, request
import sqlite3  # للتعامل مع قاعدة البيانات

# إنشاء تطبيق Flask
app = Flask(__name__)

# ===== الصفحة الرئيسية =====
@app.route('/')
def home():
    # عرض ملف index.html للمستخدم
    return render_template('index.html')

# ===== صفحة الحجز =====
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    # إذا أرسل المستخدم النموذج (POST)
    if request.method == 'POST':
        # استلام البيانات من النموذج
        name = request.form['name']         # الاسم المدخل
        email = request.form['email']       # البريد الإلكتروني
        trip = request.form['trip']         # الرحلة المختارة

        # فتح اتصال بقاعدة البيانات
        conn = sqlite3.connect('bookings.db')
        cursor = conn.cursor()

        # تنفيذ إدخال البيانات في الجدول
        cursor.execute('INSERT INTO bookings (name, email, trip) VALUES (?, ?, ?)', (name, email, trip))

        # حفظ التغييرات وإغلاق الاتصال
        conn.commit()
        conn.close()

        # رسالة تأكيد بعد الحجز
        return f"<h3>تم الحجز بنجاح! شكراً {name}</h3><a href='/'>العودة للرئيسية</a>"

    # في حالة الطلب GET، عرض نموذج الحجز
    return render_template('booking.html')

# ===== تشغيل الخادم =====
if __name__ == '__main__':
    # تشغيل التطبيق في وضع التطوير (debug)
    app.run(debug=True)