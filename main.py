from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# الصفحة الرئيسية - تعرض 3 مرشدين فقط
@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM guides")
    guides = cursor.fetchall()
    conn.close()
    return render_template('index.html', guides=guides[:3])

# صفحة جميع المرشدين
@app.route('/guides')
def show_guides():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM guides")
    guides = cursor.fetchall()
    conn.close()
    return render_template('guides.html', guides=guides)

# صفحة تفاصيل مرشد معين حسب الـ id
@app.route('/guide/<int:guide_id>')
def guide_details(guide_id):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM guides WHERE id=?", (guide_id,))
    guide = cursor.fetchone()
    conn.close()
    if guide:
        return render_template('guide_details.html', guide=guide)
    else:
        return "المرشد غير موجود", 404

# تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True)