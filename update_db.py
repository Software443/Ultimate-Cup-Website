import sqlite3

conn = sqlite3.connect('ultimate_cup.db')
cur = conn.cursor()

# # 1. Rename the old table
# cur.execute("ALTER TABLE team_ratings RENAME TO team_ratings_old;")

# # 2. Create a new table with 'points' as REAL
# cur.execute("""
# CREATE TABLE team_ratings (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     team_name TEXT,
#     year INTEGER,
#     points REAL
# );
# """)

# # 3. Copy data from old table
# cur.execute("""
# INSERT INTO team_ratings (team_name, year, points)
# SELECT team_name, year, CAST(points AS REAL) FROM team_ratings_old;
# """)

# # 4. Drop old table
# cur.execute("DROP TABLE team_ratings_old;")

# conn.commit()
# conn.close()

# print("✅ Points column successfully converted to REAL (decimal numbers supported).")
cur.execute("PRAGMA table_info(team_ratings);")