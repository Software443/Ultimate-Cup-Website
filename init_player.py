import sqlite3

conn = sqlite3.connect("ultimate_cup.db")
cursor = conn.cursor()

# Create the players table
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

# Add some sample players (optional)
players = [
    ("John Smith", 1, 3, 1, 0),
    ("Michael Johnson", 1, 2, 0, 0),
    ("Peter Obi", 2, 1, 2, 0),
    ("James Ade", 2, 0, 1, 1),
    ("Sadiq Musa", 3, 4, 0, 0)
]

cursor.executemany("INSERT INTO players (name, team_id, goals, yellow_cards, red_cards) VALUES (?, ?, ?, ?, ?)", players)

conn.commit()
conn.close()

print("✅ Players table created and populated successfully!")
