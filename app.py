from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def calculate_grade(marks):
    if marks >= 90:
        return "A+"
    elif marks >= 75:
        return "A"
    elif marks >= 60:
        return "B"
    elif marks >= 35:
        return "C"
    else:
        return "F"

def init_db():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subject TEXT NOT NULL,
            marks INTEGER NOT NULL,
            grade TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()
from flask import Flask, render_template, request, redirect, url_for

@app.route("/calculator", methods=["GET", "POST"])
def calculator():

    if request.method == "POST":
        current_value = request.form.get("current")

        if not current_value or current_value.strip() == "":
            return redirect(url_for("calculator"))

        try:
            current = int(current_value)
            passing = 35
            result = max(0, passing - current)

            # Redirect instead of render
            return redirect(url_for("calculator", result=result))

        except ValueError:
            return redirect(url_for("calculator"))

    # GET request
    result = request.args.get("result")

    return render_template("calculator.html", result=result)



@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        subject = request.form["subject"]
        marks = int(request.form["marks"])
        grade = calculate_grade(marks)

        cursor.execute("""
            UPDATE students
            SET name = ?, subject = ?, marks = ?, grade = ?
            WHERE id = ?
        """, (name, subject, marks, grade, id))

        conn.commit()
        conn.close()
        return redirect("/")

    cursor.execute("SELECT * FROM students WHERE id = ?", (id,))
    student = cursor.fetchone()
    conn.close()

    return render_template("edit.html", student=student)


@app.route("/")
def home():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    # Calculate Average
    cursor.execute("SELECT AVG(marks) FROM students")
    avg = cursor.fetchone()[0]

    # Get Topper
    cursor.execute("SELECT name, subject, marks FROM students ORDER BY marks DESC LIMIT 1")
    topper = cursor.fetchone()


    # Weak Students (below 40)
    cursor.execute("SELECT name, subject, marks FROM students WHERE marks < 35")

    weak_students = cursor.fetchall()

    # Get names and marks for chart
    cursor.execute("SELECT name, marks FROM students")
    chart_data = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    conn.close()

    return render_template(
    "index.html",
    students=students,
    average=avg,
    topper=topper,
    weak_students=weak_students,
    chart_data=chart_data,
    passing_marks=35,
    total_students=total_students
)


@app.route("/delete/<int:id>")
def delete_student(id):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form["name"]
        subject = request.form["subject"]
        marks = int(request.form["marks"])
        grade = calculate_grade(marks)

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (name, subject, marks, grade) VALUES (?, ?, ?, ?)",
            (name, subject, marks, grade)
        )
        conn.commit()
        conn.close()

        return redirect("/")


    return render_template("add.html")

if __name__ == "__main__":
    app.run()
