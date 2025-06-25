# ===== هذا الملف يقوم بإنشاء قاعدة بيانات bookings.db وجدول الحجوزات =====

import sqlite3  # مكتبة SQLite المدمجة مع بايثون

# إنشاء اتصال بقاعدة البيانات (سيتم إنشاؤها إذا لم تكن موجودة)
conn = sqlite3.connect('bookings.db')

# إنشاء مؤشر للتعامل مع قاعدة البيانات
cursor = conn.cursor()

# تنفيذ أمر إنشاء جدول الحجوزات إذا لم يكن موجودًا بالفعل
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,  -- رقم الحجز (تلقائي)
        name TEXT NOT NULL,                    -- اسم الشخص
        email TEXT NOT NULL,                   -- البريد الإلكتروني
        trip TEXT NOT NULL,                    -- اسم الرحلة
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP  -- وقت وتاريخ الحجز
    )
''')

# حفظ التغييرات
conn.commit()

# إغلاق الاتصال
conn.close()

print("✅ تم إنشاء قاعدة البيانات bookings.db بنجاح.")
