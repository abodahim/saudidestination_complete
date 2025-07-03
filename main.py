from flask import Flask, render_template, g, abort
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'database.db'

# الاتصال بقاعدة البيانات
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # حتى نستطيع الوصول للقيم كقاموس
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# الصفحة الرئيسية - عرض 3 مرشدين فقط
@app.route('/')
def index():
    db = get_db()
    cursor = db.execute("SELECT * FROM guides LIMIT 3")
    guides = cursor.fetchall()
    return render_template('index.html', guides=guides)

# صفحة جميع المرشدين
@app.route('/guides')
def all_guides():
    db = get_db()
    cursor = db.execute("SELECT * FROM guides")
    guides = cursor.fetchall()
    return render_template('guides.html', guides=guides)

# صفحة تفاصيل مرشد معين
@app.route('/guide/<int:guide_id>')
def guide_details(guide_id):
    db = get_db()
    cursor = db.execute("SELECT * FROM guides WHERE id=?", (guide_id,))
    guide = cursor.fetchone()
    if guide is None:
        abort(404)
    return render_template('guide_details.html', guide=guide)

# تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True)