from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup
def init_db():
    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            time TEXT,
            start_date TEXT,
            end_date TEXT
        )''')
init_db()

# Route: login/signup
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        action = request.form.get("action")
        username = request.form.get("username")
        password = request.form.get("password")

        con = sqlite3.connect("database.db")
        cur = con.cursor()

        if action == "signup":
            try:
                cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                            (username, generate_password_hash(password)))
                con.commit()
                session["user_id"] = cur.lastrowid
                return redirect("/home")
            except:
                return "Username already exists!"
        elif action == "signin":
            cur.execute("SELECT id, password FROM users WHERE username = ?", (username,))
            user = cur.fetchone()
            if user and check_password_hash(user[1], password):
                session["user_id"] = user[0]
                return redirect("/home")
            return "Invalid credentials."
    return render_template("login.html")

# Route: home page
@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect("/")
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM medicines WHERE user_id = ?", (session["user_id"],))
    medicines = cur.fetchall()
    return render_template("index.html", medicines=medicines)

# Route: add medicine
@app.route("/add", methods=["POST"])
def add():
    if "user_id" not in session:
        return redirect("/")
    name = request.form["name"]
    time = request.form["time"]
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO medicines (user_id, name, time, start_date, end_date) VALUES (?, ?, ?, ?, ?)", 
                (session["user_id"], name, time, start_date, end_date))
    con.commit()
    return redirect("/home")

# Route: delete medicine
@app.route("/delete/<int:id>")
def delete(id):
    if "user_id" not in session:
        return redirect("/")
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("DELETE FROM medicines WHERE id = ? AND user_id = ?", (id, session["user_id"]))
    con.commit()
    return redirect("/home")

# Route: provide data for JS
@app.route("/get_medicines")
def get_medicines():
    if "user_id" not in session:
        return jsonify([])
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("SELECT id, time, start_date, end_date FROM medicines WHERE user_id = ?", (session["user_id"],))
    return jsonify(cur.fetchall())

if __name__ == "__main__":
    app.run(debug=True)
