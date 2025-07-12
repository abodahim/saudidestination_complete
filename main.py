from flask import Flask, render_template, request

app = Flask(__name__)

# الصفحة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# صفحة تفاصيل الرحلة (تم إصلاحها)
@app.route('/trip/<trip_name>')
def trip_details(trip_name):
    return render_template('trip_details.html', trip_name=trip_name)

if __name__ == '__main__':
    app.run(debug=True)