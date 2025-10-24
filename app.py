from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import pandas as pd
import json                # only needed if you still use json elsewhere
import plotly
import plotly.express as px
import plotly.io as pio    # <- for reliable serialization

import os
from werkzeug.utils import secure_filename




app = Flask(__name__)
app.secret_key = "ultimatecup_secret"

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---------- Database Connection ----------
def get_db():
    conn = sqlite3.connect("ultimate_cup.db")
    conn.row_factory = sqlite3.Row
    return conn


# ---------- Home ----------
@app.route('/')
def index():
    return render_template('index.html')


# ---------- User Dashboard ----------
@app.route('/user')
def user_dashboard():
    conn = get_db()
    # df = pd.read_sql_query("SELECT * FROM team_ratings", conn)
    df = pd.read_sql_query("""
        SELECT r.team_name, r.year, r.points, t.badge
        FROM team_ratings r
        LEFT JOIN teams t ON r.team_name = t.name
        ORDER BY r.points DESC
    """, conn)
    conn.close()

    if df.empty:
        conn.close()
        return render_template('user_dashboard.html', year=None, table=[], graphJSON=None)

    # --- Extract available years ---
    years = sorted(df["year"].unique().tolist(), reverse=True)

    # --- Get selected year from query params ---
    selected_year = request.args.get('year', years[0])  # default to latest
    selected_year = int(selected_year)

    # --- Filter by year ---
    df_year = df[df["year"] == selected_year].sort_values(by="points", ascending=False)
    df_year["Rank"] = range(1, len(df_year) + 1)

    # --- Create bar chart ---
    fig = px.bar(
        df_year,
        x="team_name",
        y="points",
        color="team_name",
        title=f"{selected_year} Ultimate Cup Team Ratings",
        text="points"
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(showlegend=False)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    conn.close()

    return render_template(
        'user_dashboard.html',
        year=selected_year,
        years=years,
        table=df_year.to_dict(orient='records'),
        graphJSON=graphJSON
    )
def get_team_performance():
    conn = get_db()
    cur = conn.cursor()

    query = """
        SELECT 
            t.id,
            t.name,
            SUM(CASE WHEN (m.team_a = t.id AND m.score_a > m.score_b)
                      OR (m.team_b = t.id AND m.score_b > m.score_a) THEN 1 ELSE 0 END) AS wins,
            SUM(CASE WHEN (m.team_a = t.id AND m.score_a < m.score_b)
                      OR (m.team_b = t.id AND m.score_b < m.score_a) THEN 1 ELSE 0 END) AS losses,
            SUM(CASE WHEN m.score_a = m.score_b THEN 1 ELSE 0 END) AS draws,
            COUNT(m.id) AS total_matches
        FROM teams t
        LEFT JOIN matches m ON t.id IN (m.team_a, m.team_b)
        GROUP BY t.id, t.name
    """

    results = cur.execute(query).fetchall()
    conn.close()

    performance = []
    for row in results:
        total = row["total_matches"]
        win_percent = (row["wins"] / total * 100) if total > 0 else 0
        performance.append({
            "team": row["name"],
            "wins": row["wins"],
            "losses": row["losses"],
            "draws": row["draws"],
            "total": total,
            "win_percent": round(win_percent, 1)
        })

@app.route('/team_summary')
def team_summary():
    team_name = request.args.get('team')
    if not team_name:
        return {"error": "No team provided"}, 400

    conn = get_db()
    cur = conn.cursor()

    # Find team ID
    cur.execute("SELECT id FROM teams WHERE name = ?", (team_name,))
    team = cur.fetchone()
    if not team:
        conn.close()
        return {"error": "Team not found"}, 404

    team_id = team["id"]

    # Fetch matches involving the team
    matches = cur.execute("""
        SELECT team_a, team_b, score_a, score_b
        FROM matches
        WHERE team_a = ? OR team_b = ?
    """, (team_id, team_id)).fetchall()

    wins = losses = draws = 0
    for m in matches:
        if m["team_a"] == team_id:
            if m["score_a"] > m["score_b"]:
                wins += 1
            elif m["score_a"] < m["score_b"]:
                losses += 1
            else:
                draws += 1
        elif m["team_b"] == team_id:
            if m["score_b"] > m["score_a"]:
                wins += 1
            elif m["score_b"] < m["score_a"]:
                losses += 1
            else:
                draws += 1

    total = wins + losses + draws
    win_percentage = (wins / total * 100) if total > 0 else 0

    conn.close()
    return {
        "team": team_name,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "win_percentage": win_percentage
    }


    # 🔽 Sort teams by win percentage (highest first)
    performance.sort(key=lambda x: x["win_percent"], reverse=True)

    return performance



# ---------- Admin Login ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == '1234':
            session['logged_in'] = True   # 👈 match this key with admin route
            flash('Welcome back, Admin!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')


# # ---------- Admin Dashboard ----------
@app.route('/admin')
def admin_dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    teams = conn.execute("SELECT * FROM teams").fetchall()
    players = conn.execute("""
        SELECT p.*, t.name AS team_name
        FROM players p
        LEFT JOIN teams t ON p.team_id = t.id
    """).fetchall()
    matches = conn.execute("""
        SELECT m.*, t1.name AS team_a_name, t2.name AS team_b_name
        FROM matches m
        JOIN teams t1 ON m.team_a = t1.id
        JOIN teams t2 ON m.team_b = t2.id
    """).fetchall()
    conn.close()
    return render_template('admin_dashboard.html', teams=teams, players=players, matches=matches)

from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = os.path.join('static', 'badges')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- API: Get Players by Team ----------
@app.route('/get_players/<int:team_id>')
def get_players(team_id):
    conn = get_db()
    players = conn.execute("SELECT id, name FROM players WHERE team_id = ?", (team_id,)).fetchall()
    conn.close()
    return {"players": [dict(p) for p in players]}


# -------------Add team-------------------
@app.route('/add_team', methods=['POST'])
def add_team():
    try:
        name = request.form['name']
        year = int(request.form['year'])
        points = float(request.form['points'])
        badge = request.files.get('badge')

        badge_path = None
        if badge and badge.filename != '':
            badge_path = f"static/badges/{badge.filename}"
            badge.save(badge_path)

        conn = get_db()
        cur = conn.cursor()

        # Check if team exists
        cur.execute("SELECT id FROM teams WHERE name = ?", (name,))
        team = cur.fetchone()
        if team is None:
            cur.execute("INSERT INTO teams (name, badge) VALUES (?, ?)", (name, badge_path))
            conn.commit()

        # Check if team rating already exists for that year
        cur.execute("SELECT id FROM team_ratings WHERE team_name = ? AND year = ?", (name, year))
        existing = cur.fetchone()

        if existing:
            cur.execute("""
                UPDATE team_ratings 
                SET points = ? 
                WHERE team_name = ? AND year = ?
            """, (points, name, year))
            flash(f"✅ {name}'s points updated for {year}.", "success")
        else:
            cur.execute("""
                INSERT INTO team_ratings (team_name, year, points)
                VALUES (?, ?, ?)
            """, (name, year, points))
            flash(f"✅ {name} added successfully for {year}.", "success")

        conn.commit()
        conn.close()

    except Exception as e:
        flash(f"❌ Error adding team: {e}", "error")

    return redirect(url_for('admin_dashboard'))

# ---------- Add Player ----------
@app.route('/add_player', methods=['GET', 'POST'])
def add_player():
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        team_id = request.form['team_id']
        goals = request.form.get('goals', 0)
        yellow_cards = request.form.get('yellow_cards', 0)
        red_cards = request.form.get('red_cards', 0)

        cur.execute("""
            INSERT INTO players (name, team_id, goals, yellow_cards, red_cards)
            VALUES (?, ?, ?, ?, ?)
        """, (name, team_id, goals, yellow_cards, red_cards))

        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))

    # If GET: fetch all teams for dropdown
    teams = cur.execute("SELECT id, name FROM teams").fetchall()
    conn.close()
    return render_template('add_player.html', teams=teams)


# ---------- Edit Player ----------
@app.route('/edit_player/<int:id>', methods=['GET', 'POST'])
def edit_player(id):
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        goals = request.form.get('goals', 0)
        yellow_cards = request.form.get('yellow_cards', 0)
        red_cards = request.form.get('red_cards', 0)

        cur.execute("""
            UPDATE players 
            SET goals = ?, yellow_cards = ?, red_cards = ?
            WHERE id = ?
        """, (goals, yellow_cards, red_cards, id))

        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))

    # If GET, fetch player info
    player = cur.execute("SELECT * FROM players WHERE id = ?", (id,)).fetchone()
    conn.close()
    return render_template('edit_player.html', player=player)


# ---------- Delete Player ----------
@app.route('/delete_player/<int:id>', methods=['GET'])
def delete_player(id):
    conn = get_db()
    conn.execute("DELETE FROM players WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

# ---------- Add Match Fixture ----------
@app.route('/add_match', methods=['POST'])
def add_match():
    data = request.form
    team_a = data.get('team_a')
    team_b = data.get('team_b')
    score_a = int(data.get('score_a', 0))
    score_b = int(data.get('score_b', 0))
    yellow_a = int(data.get('yellow_a', 0))
    yellow_b = int(data.get('yellow_b', 0))
    red_a = int(data.get('red_a', 0))
    red_b = int(data.get('red_b', 0))
    venue = data.get('venue')
    date = data.get('date')
    stage = data.get('stage')
    year = date.split("-")[0] if date else "2025"

    conn = get_db()
    cur = conn.cursor()

    # Insert match
    cur.execute("""
        INSERT INTO matches (team_a, team_b, score_a, score_b, yellow_a, yellow_b, red_a, red_b, venue, date, stage, year)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (team_a, team_b, score_a, score_b, yellow_a, yellow_b, red_a, red_b, venue, date, stage, year))
    match_id = cur.lastrowid

    # Insert goal scorers
    scorers = data.getlist('scorers[]')
    goals_a = data.getlist('goals_a[]')
    goals_b = data.getlist('goals_b[]')

    # Handle scorers for both teams
    for i, player_id in enumerate(scorers):
        if player_id:
            goals_scored = 1
            # determine if from team A or B
            if i < len(goals_a):
                goals_scored = int(goals_a[i]) if goals_a[i] else 1
            elif i < len(goals_b):
                goals_scored = int(goals_b[i]) if goals_b[i] else 1

            cur.execute("""
                INSERT INTO match_goals (match_id, player_id, goals_scored)
                VALUES (?, ?, ?)
            """, (match_id, player_id, goals_scored))

    conn.commit()
    conn.close()

    flash("✅ Match and scorers added successfully!", "success")
    return redirect(url_for('admin_dashboard'))


# ---------- Matches Page ----------
@app.route('/matches')
def matches():
    conn = get_db()

    # 🔹 Get all available years from the matches table
    years = [row['year'] for row in conn.execute("SELECT DISTINCT year FROM matches ORDER BY year DESC").fetchall()]

    # 🔹 Filters
    selected_year = request.args.get('year')
    selected_stage = request.args.get('stage')

    # 🔹 Base query
    query = """
        SELECT 
            m.id, m.team_a, m.team_b, m.score_a, m.score_b,
            m.yellow_a, m.yellow_b, m.red_a, m.red_b,
            m.stage, m.date, m.venue, m.year,
            t1.name AS team_a_name, t2.name AS team_b_name
        FROM matches m
        JOIN teams t1 ON m.team_a = t1.id
        JOIN teams t2 ON m.team_b = t2.id
    """
    conditions = []
    params = []

    # 🔸 Apply filters dynamically
    if selected_year:
        conditions.append("m.year = ?")
        params.append(selected_year)
    if selected_stage:
        conditions.append("m.stage = ?")
        params.append(selected_stage)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY m.date DESC"

    matches_rows = conn.execute(query, params).fetchall()
    matches_data = []

    # 🔹 Build match data + goal scorers
    for match in matches_rows:
        match = dict(match)

        scorers_query = """
            SELECT p.name AS player_name, mg.goals_scored, p.team_id
            FROM match_goals mg
            JOIN players p ON mg.player_id = p.id
            WHERE mg.match_id = ?
        """
        goal_rows = conn.execute(scorers_query, (match["id"],)).fetchall()

        team_a_scorers = [f"{row['player_name']} ({row['goals_scored']})" for row in goal_rows if row["team_id"] == match["team_a"]]
        team_b_scorers = [f"{row['player_name']} ({row['goals_scored']})" for row in goal_rows if row["team_id"] == match["team_b"]]

        matches_data.append({
            "id": match["id"],
            "year": match["year"],
            "team_a": match["team_a_name"],
            "team_b": match["team_b_name"],
            "score_a": match["score_a"],
            "score_b": match["score_b"],
            "stage": match["stage"],
            "venue": match["venue"],
            "date": match["date"],
            "yellow_a": match["yellow_a"],
            "red_a": match["red_a"],
            "yellow_b": match["yellow_b"],
            "red_b": match["red_b"],
            "team_a_scorers": team_a_scorers,
            "team_b_scorers": team_b_scorers
        })

    conn.close()

    # 🔹 Render the template
    return render_template(
        'matches.html',
        matches=matches_data,
        years=years,
        selected_year=selected_year,
        selected_stage=selected_stage
    )


# @app.route('/add_team', methods=['POST'])
# def add_team():
#     if 'logged_in' not in session:
#         return redirect(url_for('login'))

#     name = request.form['name']
#     points = request.form.get('points', 0)
#     badge_file = request.files.get('badge')

#     badge_path = None
#     if badge_file and badge_file.filename != '':
#         filename = secure_filename(badge_file.filename)
#         badge_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         badge_file.save(badge_path)

#     conn = get_db()
#     conn.execute("""
#         INSERT INTO teams (name, points, badge_path)
#         VALUES (?, ?, ?)
#     """, (name, points, badge_path))
#     conn.commit()
#     conn.close()
#     return redirect(url_for('admin_dashboard'))


# ---------- Add New Team ----------
# @app.route('/add_team', methods=['GET', 'POST'])
# def add_team():
#     if not session.get('logged_in'):
#         return redirect(url_for('login'))

#     if request.method == 'POST':
#         team_name = request.form['team_name']
#         year = request.form['year']
#         points = request.form['points']

#         conn = get_db()
#         conn.execute("INSERT INTO team_ratings (team_name, year, points) VALUES (?, ?, ?)",
#                      (team_name, year, points))
#         conn.commit()
#         conn.close()

#         return redirect(url_for('admin_dashboard'))

#     return render_template('add_team.html')


# ---------- Edit Team ----------
# @app.route('/edit_team/<int:team_id>', methods=['GET', 'POST'])
# def edit_team(team_id):
#     if not session.get('logged_in'):
#         return redirect(url_for('login'))

#     conn = get_db()
#     team = conn.execute("SELECT * FROM team_ratings WHERE id = ?", (team_id,)).fetchone()

#     if request.method == 'POST':
#         team_name = request.form['team_name']
#         year = request.form['year']
#         points = request.form['points']

#         conn.execute("UPDATE team_ratings SET team_name = ?, year = ?, points = ? WHERE id = ?",
#                      (team_name, year, points, team_id))
#         conn.commit()
#         conn.close()
#         return redirect(url_for('admin_dashboard'))

#     conn.close()
#     return render_template('edit_team.html', team=team)


# # ---------- Delete Team ----------
# @app.route('/delete_team/<int:team_id>')
# def delete_team(team_id):
#     if not session.get('logged_in'):
#         return redirect(url_for('login'))

#     conn = get_db()
#     conn.execute("DELETE FROM team_ratings WHERE id = ?", (team_id,))
#     conn.commit()
#     conn.close()

#     return redirect(url_for('admin_dashboard'))


# ---------- EDIT & DELETE ROUTES ----------

# ---- TEAMS ----
@app.route('/edit_team/<int:id>', methods=['POST'])
def edit_team(id):
    conn = get_db()
    conn.execute("""
        UPDATE teams 
        SET name = ?, coach = ?, year_established = ?, badge = ?
        WHERE id = ?
    """, (
        request.form['name'],
        request.form.get('coach'),
        request.form.get('year_established'),
        request.form.get('badge'),
        id
    ))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))


@app.route('/delete_team/<int:id>', methods=['POST'])
def delete_team(id):
    conn = get_db()
    conn.execute("DELETE FROM teams WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))


# ---- PLAYERS ----
# @app.route('/edit_player/<int:id>', methods=['POST'])
# def edit_player(id):
#     conn = get_db()
#     conn.execute("""
#         UPDATE players
#         SET name = ?, team_id = ?, goals = ?, yellow_cards = ?, red_cards = ?
#         WHERE id = ?
#     """, (
#         request.form['name'],
#         request.form['team_id'],
#         request.form.get('goals', 0),
#         request.form.get('yellow_cards', 0),
#         request.form.get('red_cards', 0),
#         id
#     ))
#     conn.commit()
#     conn.close()
#     return redirect(url_for('admin_dashboard'))


# @app.route('/delete_player/<int:id>', methods=['POST'])
# def delete_player(id):
#     conn = get_db()
#     conn.execute("DELETE FROM players WHERE id = ?", (id,))
#     conn.commit()
#     conn.close()
#     return redirect(url_for('admin_dashboard'))


# ---- MATCHES ----
# ---------- EDIT MATCH FIXTURE ----------
@app.route('/edit_match/<int:match_id>', methods=['GET', 'POST'])
def edit_match(match_id):
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        cur.execute("""
            UPDATE matches
            SET team_a = ?, team_b = ?, score_a = ?, score_b = ?, stage = ?, venue = ?, date = ?
            WHERE id = ?
        """, (
            request.form['team_a'],
            request.form['team_b'],
            request.form['score_a'],
            request.form['score_b'],
            request.form['stage'],
            request.form['venue'],
            request.form['date'],
            match_id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))

    # If GET: show edit form
    match = cur.execute("SELECT * FROM matches WHERE id = ?", (match_id,)).fetchone()
    teams = cur.execute("SELECT id, name FROM teams").fetchall()
    conn.close()

    return render_template('edit_match.html', match=match, teams=teams)



# ---------- DELETE MATCH FIXTURE ----------
@app.route('/delete_match/<int:match_id>', methods=['POST'])
def delete_match(match_id):
    conn = get_db()
    conn.execute("DELETE FROM matches WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("🗑️ Match fixture deleted successfully.", "info")
    return redirect(url_for('admin_dashboard'))





# ---------- Logout ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
