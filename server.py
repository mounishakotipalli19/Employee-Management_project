from flask import Flask, request, redirect, render_template, make_response, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# ------ Flask application ------
app = Flask(__name__)
app.secret_key = "employee-management-secret-key"


# ------ Database connection ------
def get_database_connection():
    connection = sqlite3.connect("users.db")
    connection.row_factory = sqlite3.Row
    return connection


# ------ Create database ------
def create_database():
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    # ------ User table ------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # ------ Employees table ------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            department TEXT NOT NULL,
            salary INTEGER NOT NULL,
            joining_date TEXT NOT NULL,
            address TEXT
        )
    """)

    connection.commit()
    connection.close()

    print("=================================")
    print("Database ready")
    print("=================================")


# ------ Login required ------
def login_required():
    return "user_id" in session


# ------ Set theme ------
@app.route("/set-theme/<theme>")
def set_theme(theme):
    if theme not in ["light", "dark"]:
        theme = "light"

    previous_page = request.referrer or "/"

    response = make_response(
        redirect(previous_page)
    )

    response.set_cookie(
        "theme",
        theme,
        max_age=60 * 60 * 24 * 365
    )

    return response


# ------ Home page ------
@app.route("/")
def home():
    if not login_required():
        return redirect("/login")

    theme = request.cookies.get("theme", "light")
    username = session.get("username")
    fullname = session.get("fullname")

    return render_template(
        "navbar.html",
        theme=theme,
        username=username,
        fullname=fullname
    )


# ------ Registration page ------
@app.route("/registerdemo", methods=["GET"])
def register_page():
    theme = request.cookies.get("theme", "light")

    return render_template(
        "registerdemo.html",
        theme=theme
    )


@app.route("/registerdemo", methods=["POST"])
def register():
    print("Register route called")

    fullname = request.form.get("fullname", "").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    theme = request.cookies.get("theme", "light")

    # ------ Validation ------
    if not fullname:
        return render_template(
            "registerdemo.html",
            theme=theme,
            error="Full name is required."
        )

    if not username:
        return render_template(
            "registerdemo.html",
            theme=theme,
            error="Username is required."
        )

    if not password:
        return render_template(
            "registerdemo.html",
            theme=theme,
            error="Password is required."
        )

    # ------ Hash password ------
    hashed_password = generate_password_hash(password)

    # ------ Insert user ------
    connection = get_database_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO users
            (
                fullname,
                username,
                password
            )
            VALUES (?, ?, ?)
        """, (
            fullname,
            username,
            hashed_password
        ))

        connection.commit()

    except sqlite3.IntegrityError:
        connection.close()

        return render_template(
            "registerdemo.html",
            theme=theme,
            error="Username already exists."
        )

    connection.close()

    return redirect("/login")


# ------ Login page ------
@app.route("/login", methods=["GET"])
def login_page():
    if "user_id" in session:
        return redirect("/")

    theme = request.cookies.get("theme", "light")

    return render_template(
        "login.html",
        theme=theme
    )


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    theme = request.cookies.get("theme", "light")

    # ------ Validation ------
    if not username or not password:
        return render_template(
            "login.html",
            theme=theme,
            error="Username and password are required."
        )

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            fullname,
            username,
            password
        FROM users
        WHERE username = ?
    """, (username,))

    user = cursor.fetchone()
    connection.close()

    # ------ User not found ------
    if user is None:
        return render_template(
            "login.html",
            theme=theme,
            error="Username or password is incorrect."
        )

    # ------ Check password ------
    password_correct = check_password_hash(
        user["password"],
        password
    )

    if not password_correct:
        return render_template(
            "login.html",
            theme=theme,
            error="Username or password is incorrect."
        )

    # ------ Login successful ------
    session.clear()

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["fullname"] = user["fullname"]

    return redirect("/")


# ------ Logout ------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ------ Add employee page ------
@app.route("/addemployee", methods=["GET"])
def add_employee_page():
    if not login_required():
        return redirect("/login")

    theme = request.cookies.get("theme", "light")

    return render_template(
        "addemployee.html",
        theme=theme
    )


@app.route("/addemployee", methods=["POST"])
def add_employee():
    if not login_required():
        return redirect("/login")

    employeename = request.form.get(
        "employeename", ""
    ).strip()

    email = request.form.get(
        "email", ""
    ).strip()

    phone = request.form.get(
        "phone", ""
    ).strip()

    department = request.form.get(
        "department", ""
    ).strip()

    salary = request.form.get(
        "salary", ""
    ).strip()

    joining = request.form.get(
        "joining", ""
    ).strip()

    address = request.form.get(
        "address", ""
    ).strip()

    # ------ Validation ------
    if not employeename:
        return "Name is required!"

    if not email:
        return "Email is required!"

    if not phone:
        return "Phone is required!"

    if not department:
        return "Department is required!"

    if not salary:
        return "Salary is required!"

    if not joining:
        return "Joining date is required!"

    try:
        salary = int(salary)
    except ValueError:
        return "Salary must be a number!"

    if salary <= 0:
        return "Salary must be greater than zero!"

    # ------ Insert employee ------
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO employees
        (
            name,
            email,
            phone,
            department,
            salary,
            joining_date,
            address
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        employeename,
        email,
        phone,
        department,
        salary,
        joining,
        address
    ))

    connection.commit()
    connection.close()

    return redirect("/employees")


# ------ Employees ------
@app.route("/employees")
def employees():
    if not login_required():
        return redirect("/login")

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM employees
        ORDER BY id DESC
    """)

    employees = cursor.fetchall()
    connection.close()

    theme = request.cookies.get("theme", "light")

    return render_template(
        "employees.html",
        employees=employees,
        theme=theme
    )


# ------ Search employee ------
@app.route("/search")
def search():
    if not login_required():
        return redirect("/login")

    search_text = request.args.get(
        "q", ""
    ).strip()

    connection = get_database_connection()
    cursor = connection.cursor()

    if search_text:
        search_value = f"%{search_text}%"

        cursor.execute("""
            SELECT *
            FROM employees
            WHERE
                name LIKE ?
                OR email LIKE ?
                OR phone LIKE ?
                OR department LIKE ?
            ORDER BY id DESC
        """, (
            search_value,
            search_value,
            search_value,
            search_value
        ))

    else:
        cursor.execute("""
            SELECT *
            FROM employees
            ORDER BY id DESC
        """)

    employees = cursor.fetchall()
    connection.close()

    theme = request.cookies.get("theme", "light")

    return render_template(
        "employees.html",
        employees=employees,
        theme=theme,
        search_text=search_text
    )


# ------ Delete employee ------
@app.route("/delete-employee/<int:id>")
def delete_employee(id):
    if not login_required():
        return redirect("/login")

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM employees
        WHERE id = ?
    """, (id,))

    connection.commit()
    connection.close()

    return redirect("/employees")


# ------ Edit employee page ------
@app.route("/edit-employee/<int:id>", methods=["GET"])
def edit_employee_page(id):
    if not login_required():
        return redirect("/login")

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM employees
        WHERE id = ?
    """, (id,))

    employee = cursor.fetchone()
    connection.close()

    if employee is None:
        return """
        <h2>Employee not found!</h2>
        <a href="/employees">
            Back to Employees
        </a>
        """

    theme = request.cookies.get(
        "theme",
        "light"
    )

    return render_template(
        "edit-employee.html",
        employee=employee,
        theme=theme
    )


@app.route("/edit-employee/<int:id>", methods=["POST"])
def edit_employee(id):
    if not login_required():
        return redirect("/login")

    employeename = request.form.get(
        "employeename", ""
    ).strip()

    email = request.form.get(
        "email", ""
    ).strip()

    phone = request.form.get(
        "phone", ""
    ).strip()

    department = request.form.get(
        "department", ""
    ).strip()

    salary = request.form.get(
        "salary", ""
    ).strip()

    joining = request.form.get(
        "joining", ""
    ).strip()

    address = request.form.get(
        "address", ""
    ).strip()

    # ------ Validation ------
    if not employeename:
        return "Name is required!"

    if not email:
        return "Email is required!"

    if not phone:
        return "Phone is required!"

    if not department:
        return "Department is required!"

    if not salary:
        return "Salary is required!"

    if not joining:
        return "Joining date is required!"

    try:
        salary = int(salary)
    except ValueError:
        return "Salary must be a number!"

    if salary <= 0:
        return "Salary must be greater than zero!"

    # ------ Update employee ------
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE employees
        SET
            name = ?,
            email = ?,
            phone = ?,
            department = ?,
            salary = ?,
            joining_date = ?,
            address = ?
        WHERE id = ?
    """, (
        employeename,
        email,
        phone,
        department,
        salary,
        joining,
        address,
        id
    ))

    connection.commit()
    connection.close()

    return redirect("/employees")


# ------ Start application ------
if __name__ == "__main__":
    create_database()
    app.run(debug=True)

