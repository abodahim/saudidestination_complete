import sqlite3

conn = sqlite3.connect('trips.db')

# إنشاء جدول الرحلات
conn.execute('''
CREATE TABLE IF NOT EXISTS trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    image TEXT
)
''')

# إضافة بيانات أولية
trips = [
    ('جدة', 'رحلة إلى مدينة جدة تشمل زيارة كورنيش جدة وواجهة البلد التاريخية.', 'jeddah_1.JPG'),
    ('الرياض', 'استمتع بجولة سياحية في الرياض تشمل برج المملكة والمتحف الوطني.', 'riyadh_1.JPG'),
    ('ينبع', 'جولة بحرية ممتعة في ينبع مع فعاليات شاطئية ومغامرات.', 'yanbu_1.JPG')
]

conn.executemany('INSERT INTO trips (name, description, image) VALUES (?, ?, ?)', trips)

conn.commit()
conn.close()

print("تم إنشاء قاعدة البيانات بنجاح")
