from flask import Flask,request,redirect,render_template,make_response,session
import sqlite3
from werkzeug.security import generate_password_hash,check_password_hash
app=Flask(__name__)
app.secret_key="employee-management-secret-key"
def get_database_connection():
    connection=sqlite3.connect("users.db")
    connection.row_factory=sqlite3.Row
    return connection
def create_database():
    #connect to database
     connection=sqlite3.connect("users.db")
    #store databse in some object
     cursor=connection.cursor()
    #write query using that object
     cursor.execute("""
                             CREATE TABLE IF NOT EXISTS users(
                             id integer PRIMARY KEY AUTOINCREMENT,
                             fullname text NOT NULL,
                             username text UNIQUE NOT NULL,
                             password text NOT NULL)""")
    #-----employee table----
     cursor.execute("""
                    CREATE TABLE IF NOT EXISTS employees(
                    id integer PRIMARY KEY AUTOINCREMENT,
                    employeename text NOT NULL,
                    email text UNIQUE NOT NULL,
                    phone TEXT NOT NULL,
                    department text NOT NULL,
                    salary INTEGER NOT NULL,
                    joining TEXT NOT NULL,
                    address TEXT
                    )""")
     
     
     
    #commit query
     connection.commit()
    #close connection
     connection.close()
     #login check
def login_required():
     return "user_id" in session
 #--set theme---#
@app.route("/set-theme/<theme>")
def set_theme(theme):
    if theme not in["light","dark"]:
       theme="light"
    previous_page=request.referrer or"/"
    response=make_response(
           redirect(previous_page)
       )
    response.set_cookie(
               "theme",
               theme,
               max_age=60*60*24*365
               )
    return response   
@app.route("/")
def home():
    if not login_required():
      return redirect("/login")
    theme=request.cookies.get(
        "theme","light"
    )
    username=session.get("username")
    fullname=session.get("fullname")
    return render_template(
            "nav.html",
             theme=theme,
             username=username,
             fullname=fullname
    )
#------home page---
@app.route("/home")
def home_page():
    return render_template("home.html")
#----register page-----
@app.route("/registerdemo",methods=["get"])
def register_page():
    theme=request.cookies.get(
        "theme",
        "light"
    )
    return render_template("registerdemo.html",theme=theme)

@app.route("/registerdemo",methods=["post"])
def register():
    fullname=request.form.get("fullname"," ").strip()
    username=request.form.get("username"," ").strip()
    password=request.form.get("password"," ")
    if not fullname:
        return render_template(
            "registerdemo.html",
            theme=request.cookies.get("theme","light"),
            error="fullname is required"
        )
    if not username:
            return render_template(
                "registerdemo.html",
                theme=request.cookies.get("theme","light"),
                error="username is required"
            )
    if not password:
            return render_template(
                "registerdemo.html",
                theme=request.cookies.get("theme","light"),
                error="password is required"
            )
#hash password
    hashed_password=generate_password_hash(password)
#insert user
    connection=get_database_connection()
    cursor=connection.cursor()
    try:
        cursor.execute("""
        INSERT INTO users(fullname,username,password)
        VALUES(?,?,?)
         """,(fullname,username,hashed_password)
         )
        connection.commit()
    except sqlite3.IntegrityError:
         connection.close()
         return render_template("registerdemo.html",theme=request.cookies.get("theme","light"),
                           error="username already existed")
    connection.close()
    return redirect("/login")
#----login page----
@app.route("/login" ,methods=["get"]) 
def login_page():
    if "user_id" in session:
        return redirect("/")
    theme=request.cookies.get("theme","light")
    return render_template("login.html",theme=theme)

@app.route("/login",methods=["post"])
def login():
    username=request.form.get("username"," ").strip()
    password=request.form.get("password"," ")
    if not username or not password:
        return render_template("login.html",theme=request.cookies.get("theme","light"),
                               error="username or password are required")
    connection=get_database_connection()
    cursor=connection.cursor()
    cursor.execute("""
         SELECT id,fullname,username,password FROM users
         WHERE username=? 
         """,(username,))
    user=cursor.fetchone()
    connection.close()
    if  user is None:
        return render_template("login.html",theme=request.cookies.get("theme","light"),
                           error="username or password is incorrect")
    password_correct=check_password_hash(user["password"],password)
    if not password_correct:
        return render_template("login.html",theme=request.cookies.get("theme","light"),
                                      error="username or password is incorrect")
    session.clear()
    session["user_id"]=user["id"]
    session["username"]=user["username"]
    session["fullname"]=user["fullname"]
    return redirect("/")
    # ----logout-----
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
 #----add employee-----
@app.route("/addemployee",methods=["get"])
def addemployee_page():
    if not login_required():
        return redirect("/login")
    theme=request.cookies.get("theme","light")
    return render_template("addemployee.html",theme=theme) 
@app.route("/addemployee",methods=["post"])
def addemployee():
    if not login_required():
        return redirect("/login")
    employeename=request.form.get("employeename").strip()
    email=request.form.get("email").strip() 
    phone=request.form.get("phone").strip()  
    department=request.form.get("department").strip()  
    salary=request.form.get("salary").strip()  
    joining=request.form.get("joining").strip()  
    address=request.form.get("address").strip()
    #validation
    if not employeename:
      return"employeename is required!"
    
    if not email:
              return"email is required!"
    if not phone:
                return"phone is required!"
    if not department:
                  return"department is required!"
    if not salary:
                    return"salary is required!"
    if not joining:
                      return"joining is required!"
    try:
        salary=int(salary)
    except ValueError:
        return "salary must be a number!"                  
    connection=get_database_connection()
    cursor=connection.cursor()
    cursor.execute("""INSERT INTO employees(
        employeename,
        email,
        phone,
        department,
        salary,
        joining,
        address) VALUES(?,?,?,?,?,?,?)
        """,(employeename,email,phone,department,salary,joining,address)) 
    connection.commit()
    connection.close()
    return redirect("/employees")


  
#-----employee page------
@app.route("/employees")
def employees():
    if not login_required():
            return redirect("/login")
    connection=get_database_connection() 
    cursor=connection.cursor()
    cursor.execute("""
                  SELECT *
                  from employees
                  ORDER BY ID ASC
                  """)
    employees=cursor.fetchall()
    connection.close()
    theme=request.cookies.get("theme","light")
    return render_template("employees.html",employees=employees,theme=theme)


#-----edit employee-----
@app.route("/edit-employee/<int:id>",methods=["get"])
def edit_employee_page(id):
    if not login_required():
        return redirect("/login")
    connection=get_database_connection()
    cursor=connection.cursor()
    cursor.execute("""
                   select * from employees
                   where id=?""",
                   (id,))
    employee=cursor.fetchone()
    connection.close()
    if employee is None:
        return"""
        <h2>employee not found</h2>
        <a href="/employees>
        Back to employees
        </a>"""
    theme=request.cookies.get("theme","light")
    return render_template("edit-employee.html",employee=employee,theme=theme)
#Edit Employee update(post)
@app.route("/edit-employee/<int:id>",methods=["post"])
def edit_employee(id):
    if not login_required():
        return redirect("/login")
    employeename=request.form.get("employeename","").strip()
    email=request.form.get("email","").strip()
    phone=request.form.get("phone","").strip()
    department=request.form.get("department","").strip()
    salary=request.form.get("salary","").strip()
    joining=request.form.get("joining","").strip()
    address=request.form.get("address","").strip()
    #validation
    if not employeename:
        return"employeename is required!"
        
    if not email:
        return"email is required!"
    if not phone:
        return"phone is required!"
    if not department:
        return"department is required!"
    if not salary:
        return"salary is required!"
    if not joining:
        return"joining is required!"
    try:
            salary=int(salary)
    except ValueError:
            return "salary must be a number!"
    connection=get_database_connection()
    cursor=connection.cursor()
    cursor.execute("""
                   UPDATE employees
                   SET
                   employeename=?,
                    email=?,
                    phone=?,
                    department=?,
                    salary=?,
                    joining=?,
                    address=?
                    WHERE id=?
                    """,(employeename,email,phone,department,salary,joining,address,id))
    connection.commit()
    connection.close()
    return redirect("/employees")
#-----deelete employee------
@app.route("/delete-employee/<int:id>")
def delete_employee(id):
    if not login_required():
            return redirect("/login")
    connection=get_database_connection()
    cursor=connection.cursor()
    cursor.execute("""
                   DELETE FROM employees
                   WHERE id=?
                   """,(id,))
    connection.commit()
    connection.close()
    return redirect("/employee")


#-----search employee------
@app.route("/search")
def search():

    if not login_required():

        return redirect("/login")

    search_text = request.args.get(
        "q",
        ""
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
        """,
        (
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

    theme = request.cookies.get(
        "theme",
        "light"
    )

    return render_template(
        "employees.html",
        employees=employees,
        theme=theme,
        search_text=search_text
    )



if __name__=="_main_":
    create_database()
    app.run(debug=True)