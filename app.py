from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "smart-campus-secret"


def get_db():
    conn = sqlite3.connect("campus.db")
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

def init_db():

    conn = get_db()

    # --------------------------------------------------
    # USERS TABLE
    # --------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'student'
        )
    """)

    # --------------------------------------------------
    # COMPLAINTS TABLE
    # --------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT DEFAULT 'Student Submitted',
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --------------------------------------------------
    # ADD STATUS COLUMNS
    # --------------------------------------------------

    existing_columns = [
        row["name"]
        for row in conn.execute(
            "PRAGMA table_info(complaints)"
        ).fetchall()
    ]

    if "maintenance_status" not in existing_columns:

        conn.execute("""
            ALTER TABLE complaints
            ADD COLUMN maintenance_status TEXT DEFAULT 'Pending'
        """)

    if "tutor_status" not in existing_columns:

        conn.execute("""
            ALTER TABLE complaints
            ADD COLUMN tutor_status TEXT DEFAULT 'Pending'
        """)

    if "hod_status" not in existing_columns:

        conn.execute("""
            ALTER TABLE complaints
            ADD COLUMN hod_status TEXT DEFAULT 'Pending'
        """)

    # --------------------------------------------------
    # NOTIFICATIONS TABLE
    # --------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER,
            sender_role TEXT,
            receiver_role TEXT,
            message TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --------------------------------------------------
    # DEFAULT STAFF ACCOUNTS
    # --------------------------------------------------

    staff_accounts = [

        (
            "System Admin",
            "admin@campus.com",
            "admin123",
            "admin"
        ),

        (
            "Maintenance Staff",
            "maintenance@campus.com",
            "maint123",
            "maintenance"
        ),

        (
            "Tutor",
            "tutor@campus.com",
            "tutor123",
            "tutor"
        ),

        (
            "Head of Department",
            "hod@campus.com",
            "hod123",
            "hod"
        )
    ]

    for staff in staff_accounts:

        existing_user = conn.execute("""
            SELECT id
            FROM users
            WHERE email=?
        """, (
            staff[1],
        )).fetchone()

        if not existing_user:

            conn.execute("""
                INSERT INTO users
                (
                    name,
                    email,
                    password,
                    role
                )
                VALUES (?, ?, ?, ?)
            """, staff)

    conn.commit()
    conn.close()


# --------------------------------------------------
# CREATE NOTIFICATION
# --------------------------------------------------

def create_notification(
    complaint_id,
    sender_role,
    receiver_role,
    message
):

    conn = get_db()

    conn.execute("""
        INSERT INTO notifications
        (
            complaint_id,
            sender_role,
            receiver_role,
            message
        )
        VALUES (?, ?, ?, ?)
    """, (
        complaint_id,
        sender_role,
        receiver_role,
        message
    ))

    conn.commit()
    conn.close()


# --------------------------------------------------
# GET NOTIFICATIONS
# --------------------------------------------------

def get_notifications(role):

    conn = get_db()

    notifications = conn.execute("""
        SELECT notifications.*, complaints.title
        FROM notifications
        LEFT JOIN complaints
        ON notifications.complaint_id = complaints.id
        WHERE receiver_role=?
        ORDER BY notifications.created_at DESC
    """, (
        role,
    )).fetchall()

    conn.close()

    return notifications


# --------------------------------------------------
# GET UNREAD NOTIFICATION COUNT
# --------------------------------------------------

def get_unread_count(role):

    conn = get_db()

    result = conn.execute("""
        SELECT COUNT(*) AS count
        FROM notifications
        WHERE receiver_role=?
        AND is_read=0
    """, (
        role,
    )).fetchone()

    conn.close()

    return result["count"]


# --------------------------------------------------
# GET ALL NOTIFICATION COUNTS
# --------------------------------------------------

def get_notification_counts():

    roles = [
        "admin",
        "maintenance",
        "tutor",
        "hod",
        "student"
    ]

    counts = {}

    for role in roles:

        counts[role] = get_unread_count(role)

    return counts


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def home():

    notification_counts = get_notification_counts()

    return render_template(
        "home.html",
        notification_counts=notification_counts
    )


# --------------------------------------------------
# REGISTER
# --------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()

        try:

            conn.execute("""
                INSERT INTO users
                (
                    name,
                    email,
                    password,
                    role
                )
                VALUES (?, ?, ?, ?)
            """, (
                name,
                email,
                password,
                "student"
            ))

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            return "Email already registered"

        conn.close()

        return redirect("/login?role=student")

    return render_template("register.html")


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    selected_role = request.args.get(
        "role",
        "student"
    )

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        selected_role = request.form.get(
            "selected_role",
            "student"
        )

        conn = get_db()

        user = conn.execute("""
            SELECT *
            FROM users
            WHERE email=?
            AND password=?
            AND role=?
        """, (
            email,
            password,
            selected_role
        )).fetchone()

        conn.close()

        if user:

            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]

            role = user["role"]

            if role == "admin":
                return redirect("/admin")

            if role == "maintenance":
                return redirect("/maintenance")

            if role == "tutor":
                return redirect("/tutor")

            if role == "hod":
                return redirect("/hod")

            return redirect("/dashboard")

        return render_template(
            "login.html",
            selected_role=selected_role,
            error="Invalid email, password or role."
        )

    return render_template(
        "login.html",
        selected_role=selected_role
    )


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# --------------------------------------------------
# STUDENT DASHBOARD
# --------------------------------------------------

@app.route("/dashboard")
def dashboard():

    if session.get("role") != "student":

        return redirect(
            "/login?role=student"
        )

    conn = get_db()

    complaints = conn.execute("""
        SELECT *
        FROM complaints
        WHERE user_id=?
        ORDER BY created_at DESC
    """, (
        session["user_id"],
    )).fetchall()

    conn.close()

    notifications = get_notifications(
        "student"
    )

    return render_template(
        "dashboard.html",
        complaints=complaints,
        notifications=notifications
    )


# --------------------------------------------------
# STUDENT SUBMIT COMPLAINT
# --------------------------------------------------

@app.route(
    "/complaint",
    methods=["GET", "POST"]
)
def complaint():

    if session.get("role") != "student":

        return redirect(
            "/login?role=student"
        )

    if request.method == "POST":

        title = request.form["title"]
        category = request.form["category"]
        description = request.form["description"]
        location = request.form["location"]
        priority = request.form["priority"]

        conn = get_db()

        cursor = conn.execute("""
            INSERT INTO complaints
            (
                title,
                category,
                description,
                location,
                priority,
                status,
                maintenance_status,
                tutor_status,
                hod_status,
                user_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title,
            category,
            description,
            location,
            priority,
            "Admin Forwarded",
            "Pending",
            "Pending",
            "Pending",
            session["user_id"]
        ))

        complaint_id = cursor.lastrowid

        conn.commit()
        conn.close()

        # Notify Admin
        create_notification(
            complaint_id,
            "student",
            "admin",
            "New complaint submitted by student."
        )

        # Notify Maintenance
        create_notification(
            complaint_id,
            "admin",
            "maintenance",
            "New complaint received. Please rectify the complaint."
        )

        return redirect("/dashboard")

    return render_template(
        "complaint.html"
    )


# --------------------------------------------------
# ADMIN
# --------------------------------------------------

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

    notifications = get_notifications(
        "admin"
    )

    return render_template(
        "admin.html",
        complaints=complaints,
        notifications=notifications
    )


# --------------------------------------------------
# MAINTENANCE
# --------------------------------------------------

@app.route("/maintenance")
def maintenance():

    if session.get("role") != "maintenance":

        return "Access denied"

    conn = get_db()

    complaints = conn.execute("""
        SELECT complaints.*, users.name
        FROM complaints
        JOIN users
        ON complaints.user_id = users.id
        WHERE maintenance_status != 'Rectified'
        AND status = 'Admin Forwarded'
        ORDER BY complaints.created_at DESC
    """).fetchall()

    conn.close()

    notifications = get_notifications(
        "maintenance"
    )

    return render_template(
        "maintenance.html",
        complaints=complaints,
        notifications=notifications
    )


# --------------------------------------------------
# MAINTENANCE RECTIFY
# --------------------------------------------------

@app.route(
    "/maintenance/rectify/<int:id>",
    methods=["POST"]
)
def maintenance_rectify(id):

    if session.get("role") != "maintenance":

        return "Access denied"

    conn = get_db()

    complaint = conn.execute("""
        SELECT *
        FROM complaints
        WHERE id=?
    """, (
        id,
    )).fetchone()

    if not complaint:

        conn.close()

        return "Complaint not found"

    conn.execute("""
        UPDATE complaints
        SET
            maintenance_status=?,
            status=?
        WHERE id=?
    """, (
        "Rectified",
        "Sent to Tutor",
        id
    ))

    conn.commit()
    conn.close()

    # Notify Admin
    create_notification(
        id,
        "maintenance",
        "admin",
        "Maintenance has rectified the complaint."
    )

    # Notify Tutor
    create_notification(
        id,
        "maintenance",
        "tutor",
        "Maintenance has rectified the complaint. Please verify the work."
    )

    return redirect(
        "/maintenance"
    )


# --------------------------------------------------
# TUTOR
# --------------------------------------------------

@app.route("/tutor")
def tutor():

    if session.get("role") != "tutor":

        return "Access denied"

    conn = get_db()

    complaints = conn.execute("""
        SELECT complaints.*, users.name
        FROM complaints
        JOIN users
        ON complaints.user_id = users.id
        WHERE maintenance_status='Rectified'
        AND tutor_status != 'Verified'
        AND status='Sent to Tutor'
        ORDER BY complaints.created_at DESC
    """).fetchall()

    conn.close()

    notifications = get_notifications(
        "tutor"
    )

    return render_template(
        "tutor.html",
        complaints=complaints,
        notifications=notifications
    )


# --------------------------------------------------
# TUTOR VERIFY
# --------------------------------------------------

@app.route(
    "/tutor/verify/<int:id>",
    methods=["POST"]
)
def tutor_verify(id):

    if session.get("role") != "tutor":

        return "Access denied"

    conn = get_db()

    complaint = conn.execute("""
        SELECT *
        FROM complaints
        WHERE id=?
    """, (
        id,
    )).fetchone()

    if not complaint:

        conn.close()

        return "Complaint not found"

    conn.execute("""
        UPDATE complaints
        SET
            tutor_status=?,
            status=?
        WHERE id=?
    """, (
        "Verified",
        "Sent to HOD",
        id
    ))

    conn.commit()
    conn.close()

    # Notify Admin
    create_notification(
        id,
        "tutor",
        "admin",
        "Tutor has verified the maintenance work."
    )

    # Notify HOD
    create_notification(
        id,
        "tutor",
        "hod",
        "Tutor has verified the complaint. Please give final approval."
    )

    return redirect(
        "/tutor"
    )


# --------------------------------------------------
# TUTOR REJECT
# --------------------------------------------------

@app.route(
    "/tutor/reject/<int:id>",
    methods=["POST"]
)
def tutor_reject(id):

    if session.get("role") != "tutor":

        return "Access denied"

    conn = get_db()

    conn.execute("""
        UPDATE complaints
        SET
            tutor_status=?,
            maintenance_status=?,
            status=?
        WHERE id=?
    """, (
        "Not Verified",
        "Pending",
        "Admin Forwarded",
        id
    ))

    conn.commit()
    conn.close()

    # Notify Admin
    create_notification(
        id,
        "tutor",
        "admin",
        "Tutor did not verify the maintenance work. Maintenance must check again."
    )

    # Notify Maintenance
    create_notification(
        id,
        "tutor",
        "maintenance",
        "Tutor did not verify the work. Please check the complaint again."
    )

    return redirect(
        "/tutor"
    )


# --------------------------------------------------
# HOD
# --------------------------------------------------

@app.route("/hod")
def hod():

    if session.get("role") != "hod":

        return "Access denied"

    conn = get_db()

    complaints = conn.execute("""
        SELECT complaints.*, users.name
        FROM complaints
        JOIN users
        ON complaints.user_id = users.id
        WHERE tutor_status='Verified'
        AND hod_status != 'Approved'
        AND status='Sent to HOD'
        ORDER BY complaints.created_at DESC
    """).fetchall()

    conn.close()

    notifications = get_notifications(
        "hod"
    )

    return render_template(
        "hod.html",
        complaints=complaints,
        notifications=notifications
    )


# --------------------------------------------------
# HOD APPROVE
# --------------------------------------------------

@app.route(
    "/hod/approve/<int:id>",
    methods=["POST"]
)
def hod_approve(id):

    if session.get("role") != "hod":

        return "Access denied"

    conn = get_db()

    complaint = conn.execute("""
        SELECT *
        FROM complaints
        WHERE id=?
    """, (
        id,
    )).fetchone()

    if not complaint:

        conn.close()

        return "Complaint not found"

    if complaint["tutor_status"] != "Verified":

        conn.close()

        return "Tutor has not verified this complaint"

    conn.execute("""
        UPDATE complaints
        SET
            hod_status=?,
            status=?
        WHERE id=?
    """, (
        "Approved",
        "Resolved",
        id
    ))

    conn.commit()
    conn.close()

    # Notify Admin
    create_notification(
        id,
        "hod",
        "admin",
        "HOD has given final approval. Complaint is resolved."
    )

    # Notify Student
    create_notification(
        id,
        "hod",
        "student",
        "Your complaint has been verified and approved by HOD. The complaint is resolved."
    )

    return redirect(
        "/hod"
    )


# --------------------------------------------------
# MARK NOTIFICATION AS READ
# --------------------------------------------------

@app.route(
    "/notifications/read/<int:id>",
    methods=["POST"]
)
def mark_notification_read(id):

    if "role" not in session:

        return redirect("/login")

    conn = get_db()

    conn.execute("""
        UPDATE notifications
        SET is_read=1
        WHERE id=?
        AND receiver_role=?
    """, (
        id,
        session["role"]
    ))

    conn.commit()
    conn.close()

    role = session["role"]

    if role == "admin":
        return redirect("/admin")

    if role == "maintenance":
        return redirect("/maintenance")

    if role == "tutor":
        return redirect("/tutor")

    if role == "hod":
        return redirect("/hod")

    return redirect("/dashboard")


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )