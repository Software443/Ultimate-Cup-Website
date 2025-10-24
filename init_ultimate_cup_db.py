import sqlite3

# Connect to the database (or create it if not found)
conn = sqlite3.connect("ultimate_cup.db")
cursor = conn.cursor()

# --------------------------
# 1️⃣ Create Teams Table
# --------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    group_name TEXT
)
""")

# Sample Teams
teams = [
    ("Lafia Stars FC", "Group A"),
    ("Kwandare United", "Group A"),
    ("Golden Boys FC", "Group A"),
    ("Bukan Sidi United", "Group B"),
    ("Doctor Academy Jr", "Group B"),
    ("Future Legends FC", "Group B"),
    ("Greater Tomorrow FC", "Group C"),
    ("Maria Assumpta FC", "Group C"),
]
cursor.executemany("INSERT INTO teams (name, group_name) VALUES (?, ?)", teams)


# --------------------------
# 2️⃣ Create Matches Table
# --------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_a INTEGER,
    team_b INTEGER,
    score_a INTEGER,
    score_b INTEGER,
    date TEXT,
    venue TEXT,
    stage TEXT,
    FOREIGN KEY (team_a) REFERENCES teams(id),
    FOREIGN KEY (team_b) REFERENCES teams(id)
)
""")

# Sample Matches
matches = [
    (1, 2, 3, 1, "2025-10-01", "Lafia City Stadium", "Group Stage"),
    (3, 1, 0, 2, "2025-10-02", "Kwandare Field", "Group Stage"),
    (4, 5, 2, 2, "2025-10-03", "Bukan Sidi Arena", "Group Stage"),
    (6, 7, 1, 0, "2025-10-05", "Youth Center Stadium", "Quarter Final"),
    (2, 6, 1, 1, "2025-10-07", "Lafia City Stadium", "Semi Final"),
    (1, 7, 2, 3, "2025-10-10", "NASPOLY Stadium", "Final")
]
cursor.executemany("""
INSERT INTO matches (team_a, team_b, score_a, score_b, date, venue, stage)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", matches)


# --------------------------
# 3️⃣ Create Players Table
# --------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    team_id INTEGER,
    goals INTEGER DEFAULT 0,
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    FOREIGN KEY (team_id) REFERENCES teams(id)
)
""")

# Sample Players
players = [
    ("John Musa", 1, 4, 1, 0),
    ("Aliyu Yakubu", 1, 2, 0, 0),
    ("Suleiman Ibrahim", 2, 1, 1, 0),
    ("Emmanuel Tega", 3, 0, 1, 0),
    ("Titus Monday", 4, 3, 0, 1),
    ("Joshua Peter", 5, 2, 0, 0),
    ("Henry Samson", 6, 3, 2, 0),
    ("Umar Danladi", 7, 1, 0, 0),
    ("Victor Kado", 8, 2, 0, 0)
]
cursor.executemany("""
INSERT INTO players (name, team_id, goals, yellow_cards, red_cards)
VALUES (?, ?, ?, ?, ?)
""", players)


# --------------------------
# 4️⃣ Create Team Ratings Table
# --------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS team_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT,
    points REAL,
    year INTEGER
)
""")

ratings = [
    ("Lafia Stars FC", 4.5, 2025),
    ("Kwandare United", 4.0, 2025),
    ("Golden Boys FC", 3.5, 2025),
    ("Doctor Academy Jr", 3.0, 2025),
    ("Bukan Sidi United", 2.75, 2025),
    ("Future Legends FC", 2.5, 2025),
    ("Greater Tomorrow FC", 2.25, 2025),
    ("Maria Assumpta FC", 1.5, 2025)
]
cursor.executemany("""
INSERT INTO team_ratings (team_name, points, year)
VALUES (?, ?, ?)
""", ratings)

# Commit and close
conn.commit()
conn.close()

print("✅ Database setup completed successfully!")
