from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

# تهيئة قاعدة البيانات
def init_db():
    conn = sqlite3.connect('visitors.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS visitors (id INTEGER PRIMARY KEY, count INTEGER)''')
    c.execute('SELECT COUNT(*) FROM visitors')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO visitors (count) VALUES (0)')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    conn = sqlite3.connect('visitors.db')
    c = conn.cursor()
    c.execute('UPDATE visitors SET count = count + 1')
    conn.commit()
    c.execute('SELECT count FROM visitors')
    visit_count = c.fetchone()[0]
    conn.close()
    return render_template('index.html', visit_count=visit_count)

@app.route('/booking')
def booking():
    return "<h1>صفحة الحجز قيد الإنشاء</h1>"

if __name__ == '__main__':
    app.run(debug=True)