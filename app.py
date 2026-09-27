from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "smart-campus-secret"


def get_db():
    conn = sqlite3.connect("campus.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'student'
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()

        try:
            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )

            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            return "Email already registered"

        conn.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        ).fetchone()

        conn.close()

        if user:

            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect("/admin")

            return redirect("/dashboard")

        return "Invalid email or password"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    complaints = conn.execute(
        "SELECT * FROM complaints WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        complaints=complaints
    )


@app.route("/complaint", methods=["GET", "POST"])
def complaint():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        title = request.form["title"]
        category = request.form["category"]
        description = request.form["description"]
        location = request.form["location"]
        priority = request.form["priority"]

        conn = get_db()

        conn.execute("""
            INSERT INTO complaints
            (title, category, description, location, priority, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            title,
            category,
            description,
            location,
            priority,
            session["user_id"]
        ))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("complaint.html")


@app.route("/admin")
def admin():

    if session.get("role") != "admin":
        return "Access denied"

    conn = get_db()

    complaints = conn.execute("""
        SELECT complaints.*, users.name
        FROM complaints
        JOIN users
        ON complaints.user_id = users.id
        ORDER BY complaints.created_at DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin.html",
        complaints=complaints
    )


@app.route("/update/<int:id>", methods=["POST"])
def update_status(id):

    if session.get("role") != "admin":
        return "Access denied"

    status = request.form["status"]

    conn = get_db()

    conn.execute(
        "UPDATE complaints SET status=? WHERE id=?",
        (status, id)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)