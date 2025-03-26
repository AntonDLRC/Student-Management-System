from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

DATABASE = "database.db"

def query_db(sql, args=(), one=False):
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute(sql, args)
    results = cursor.fetchall()
    db.commit()
    db.close()
    return (results[0] if results else None) if one else results

# admin page
@app.route("/admin")
def admin():
    sql = "SELECT Students.ID, Students.Name, Students.Image FROM Students;"
    results = query_db(sql)
    return render_template("admin.html", results = results)

# home page
@app.route("/")
def home():
    return render_template("home.html")

# student details page
@app.route("/student/<int:id>")
def student(id):
    sql = """SELECT * FROM Students 
 JOIN StudentCourses ON StudentCourses.StudentID = Students.ID
 JOIN Courses ON Courses.ID = StudentCourses.CourseID 
 WHERE Students.ID = ?;"""
    result = query_db(sql, (id,))
    return render_template("student_details.html", student = result)


if __name__ == "__main__":
    app.run(debug=True, port=5091)


