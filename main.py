from flask import Flask, render_template

# إنشاء التطبيق
app = Flask(__name__)

# الصفحة الرئيسية
@app.route('/')
def home():
    return render_template('index.html')

# صفحة الحجز (مستقبلًا)
@app.route('/booking')
def booking():
    return "<h2>صفحة الحجز قيد التطوير</h2>"

# تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True)