from flask import Flask, render_template, request, flash, session, redirect
import sqlite3
#super cool functions to generate and check password password hashes
from werkzeug.security import generate_password_hash, check_password_hash

#create app
app = Flask(__name__)

#secret key is needed for sessions and flash messages
app.config['SECRET_KEY'] = "MySecretKey"

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
    # Check if the user is logged in and is an admin
    if 'user' in session and session['user']['role'] == "admin":
        sql = "SELECT Students.ID, Students.Name, Students.Image FROM Students;"
        results = query_db(sql)
        return render_template("admin.html", results = results)
    else:
        flash("You do not have permission to access this page.")
        return redirect("/")
    
# teacher page
@app.route("/teacher/<int:id>")
def teacher(id):
    # Check if the user is logged in and is the correct teacher
    if 'user' in session and session['user']['role'] == "teacher" and session['user']['id'] == id:
        # Fetch students grouped by year levels assigned to this teacher
        sql_students_by_year = """
            SELECT Students.ID, Students.Name, Students.Age, Students.Year, Students.Image, YearLevels.Year
            FROM Students
            JOIN StudentCourses ON Students.ID = StudentCourses.StudentID
            JOIN Courses ON StudentCourses.CourseID = Courses.ID
            JOIN YearLevels ON Courses.YearLevelID = YearLevels.ID
            WHERE Courses.TeacherID = ?
        """
        students_by_year = query_db(sql_students_by_year, (id,))

        # Organize students into columns by year
        students_by_year_column = {}
        for student in students_by_year:
            year = student[-1]  # Year is the last column
            if year not in students_by_year_column:
                students_by_year_column[year] = []
            students_by_year_column[year].append(student)

        # Pass the teacher session data and students to the template
        return render_template(
            "teacher.html",
            teacher=session['user'],  # Pass the teacher data from the session
            students_by_year_column=students_by_year_column  # Students grouped by year
        )
    else:
        flash("You are not authorized to access this page.")
        return redirect("/")

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

# signup page - when a user signup, their username and password are stored in the database and the password is hashed
@app.route("/signup", methods = ["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        sql = "INSERT INTO User (username, password) VALUES (?, ?);"
        query_db(sql, (username, hashed_password))
        # flash to show that the account was created
        flash("Account created successfully!")
    return render_template("signup.html")

# login page 
@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        sql = "SELECT * FROM User WHERE username = ?"
        user = query_db(sql=sql, args=(username,), one=True)
        if user:
            if check_password_hash(user[2], password):
                # Overwrite session data with the logged-in user's information
                session.clear()  # Clear any existing session data
                #this store the username in the session
                session['user'] = { 
                    'id': user[0], 
                    'username': user[1],
                    'role': user[3] 
                    }
                print("Session set:", session)  # Debugging: Check session after login
                flash("Logged In Succesfully!")
                #redirect based on role
                if user[3] == "admin":
                    return redirect("/admin")
                elif user[3] == "teacher":
                    return redirect(f"/teacher/{user[0]}") # Redirect to teacher's dashboard
                else:
                    return redirect("/")  # Redirect to home 
            else:
                flash("Password is incorrect")
        else:
            flash("The username does not exist")
    return render_template("home.html")


# logout page
@app.route('/logout')
def logout():
    # Clear all session data
    session.clear() # session.clear removes all data from the session
    print("Session cleared", session)
    flash("You have been logged out.")
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True, port=5191)


