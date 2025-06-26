import sqlite3

# إنشاء أو فتح ملف قاعدة البيانات
conn = sqlite3.connect('create.db')

# إنشاء جدول للحجوزات إن لم يكن موجودًا
conn.execute('''
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    trip TEXT NOT NULL,
    date TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print("تم إنشاء قاعدة البيانات بنجاح.")
