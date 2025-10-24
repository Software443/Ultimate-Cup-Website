import sqlite3

# Connect (creates file if it doesn’t exist)
conn = sqlite3.connect("ultimate_cup.db")
cursor = conn.cursor()

# ---------- Create Teams Table ----------
cursor.execute("""
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
""")

# ---------- Create Matches Table ----------
cursor.execute("""
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_a INTEGER,
    team_b INTEGER,
    score_a INTEGER DEFAULT 0,
    score_b INTEGER DEFAULT 0,
    date TEXT,
    venue TEXT,
    FOREIGN KEY (team_a) REFERENCES teams(id),
    FOREIGN KEY (team_b) REFERENCES teams(id)
)
""")

# ---------- Create Team Ratings Table ----------
cursor.execute("""
CREATE TABLE IF NOT EXISTS team_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER,
    team_name TEXT,
    points REAL
)
""")

# ---------- Seed Example Data ----------
teams = [
    ("Future Legends FC",),
    ("FC Dunoma",),
    ("Greater Tomorrow FC",),
    ("Bukan Sidi United",)
]
cursor.executemany("INSERT OR IGNORE INTO teams (name) VALUES (?)", teams)

matches = [
    (1, 2, 3, 1, "2024-09-12", "Lafia Stadium"),
    (3, 4, 2, 2, "2024-09-18", "Dunoma Field"),
    (1, 3, 1, 0, "2024-10-01", "Lafia Stadium"),
    (2, 4, 0, 1, "2024-10-05", "Bukan Sidi Park")
]
cursor.executemany("""
INSERT INTO matches (team_a, team_b, score_a, score_b, date, venue)
VALUES (?, ?, ?, ?, ?, ?)
""", matches)

ratings = [
    (2024, "Future Legends FC", 8.5),
    (2024, "FC Dunoma", 6.5),
    (2024, "Greater Tomorrow FC", 4.0),
    (2024, "Bukan Sidi United", 2.5)
]
cursor.executemany("""
INSERT INTO team_ratings (year, team_name, points)
VALUES (?, ?, ?)
""", ratings)

conn.commit()
conn.close()

print("✅ Database initialized successfully!")
