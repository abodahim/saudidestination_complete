from flask import Flask, render_template

app = Flask(__name__)

# بيانات الرحلات (ثابتة مؤقتًا إلى حين ربط قاعدة البيانات)
trips = {
    1: {
        'title': 'رحلة إلى جدة',
        'description': 'استمتع بشاطئ البحر الأحمر وأنشطة الغوص.',
        'price': 350,
        'date': '2025-07-10',
        'images': ['jeddah_1.jpg', 'jeddah_2.jpg', 'jeddah_3.jpg', 'jeddah_4.jpg']
    },
    2: {
        'title': 'جولة فاخرة في الرياض',
        'description': 'تعرف على معالم العاصمة بأسلوب راقٍ.',
        'price': 400,
        'date': '2025-07-15',
        'images': ['riyadh_1.jpg', 'riyadh_2.jpg', 'riyadh_3.jpg', 'riyadh_4.jpg']
    },
    3: {
        'title': 'رحلة إلى ينبع',
        'description': 'شواطئ ساحرة وأنشطة مائية ممتعة.',
        'price': 370,
        'date': '2025-07-30',
        'images': ['yanbu_1.jpg', 'yanbu_2.jpg', 'yanbu_3.jpg', 'yanbu_4.jpg']
    }
}

# صفحة رئيسية افتراضية (يمكن تعديلها لاحقًا)
@app.route('/')
def home():
    return "<h1>مرحباً بكم في وجهة السعودية</h1><p>يرجى التوجه إلى /trip/1 أو /trip/2 لعرض تفاصيل الرحلات.</p>"

# صفحة تفاصيل الرحلة حسب رقم الرحلة
@app.route('/trip/<int:trip_id>')
def trip_details(trip_id):
    trip = trips.get(trip_id)
    if trip:
        return render_template('trip_details.html', trip=trip)
    return "الرحلة غير موجودة", 404

if __name__ == '__main__':
    app.run(debug=True)
