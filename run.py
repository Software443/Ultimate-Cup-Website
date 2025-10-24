import sqlite3

conn = sqlite3.connect("ultimate_cup.db")
cur = conn.cursor()

# Add missing columns safely
cur.execute("ALTER TABLE teams ADD COLUMN coach TEXT;")
cur.execute("ALTER TABLE teams ADD COLUMN badge TEXT;")

conn.commit()
conn.close()

print("✅ 'coach' and 'badge' columns added successfully!")