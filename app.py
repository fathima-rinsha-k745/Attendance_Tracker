from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

# ---------- DATABASE SETUP ----------
def init_db():
    if not os.path.exists("attendance.db"):
        conn = sqlite3.connect("attendance.db")
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                date TEXT,
                status TEXT,
                FOREIGN KEY(student_id) REFERENCES students(id)
            )
        """)

        conn.commit()
        conn.close()

init_db()

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("home.html", title="Home")

# ---------- ADD STUDENT ----------
@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form["name"]

        conn = sqlite3.connect("attendance.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO students (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add_student.html", title="Add Student")

# ---------- TAKE ATTENDANCE ----------
@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    conn = sqlite3.connect("attendance.db")
    cur = conn.cursor()

    if request.method == "POST":

        # FIX DUPLICATION — clear today's records BEFORE adding new
        cur.execute("DELETE FROM attendance WHERE date = DATE('now')")

        for key in request.form:
            if key.startswith("status_"):
                student_id = key.split("_")[1]
                status = request.form[key]

                cur.execute(
                    "INSERT INTO attendance (student_id, date, status) VALUES (?, DATE('now'), ?)",
                    (student_id, status)
                )

        conn.commit()
        conn.close()
        return redirect("/report")

    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    conn.close()

    return render_template("attendance.html", students=students, title="Attendance")

# ---------- CLEAR TODAY ----------
@app.route("/clear_Attendance")
def clear_Attendance():
    conn = sqlite3.connect("attendance.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM attendance WHERE date = DATE('now')")
    conn.commit()
    conn.close()

    return redirect("/attendance")


# ---------- REPORT ----------
@app.route("/report")
def report():
    conn = sqlite3.connect("attendance.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT students.name, attendance.date, attendance.status
        FROM attendance
        JOIN students ON students.id = attendance.student_id
        ORDER BY attendance.date DESC
    """)

    data = cur.fetchall()
    conn.close()

    return render_template("report.html", data=data, title="Report")

if __name__ == "__main__":
    app.run(debug=True)
