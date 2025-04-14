from flask import Flask, render_template, request, flash, session, redirect
import sqlite3
#super cool functions to generate and check password password hashes
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

DATABASE = "database.db"

#This query_db function combines getting the databse, cursor, executing and fetching the results
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
    result = query_db(sql, (id,)) #this query_db is not (sql, (id,) True) because the courses 
                                  # have multiple rows
    return render_template("student_details.html", student = result)

# signup page
@app.route("/signup", methods = ["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form("username")
        password = request.form("password")
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        sql = "INSERT INTO User (username, password) VALUES (?, ?);"
        query_db(sql, (username, hashed_password))
        # flash to show that the account was created
        flash("Account created successfully!")


if __name__ == "__main__":
    app.run(debug=True, port=5090)


