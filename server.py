from flask import Flask,request,redirect,render_template,make_response,session
import sqlite3 
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
          id integer PRIMARY KEY autoincrement,
          fullname text not null,
          username text unique not null,
          password text not null)""")
    cursor.execute(""" 
                   CREATE TABLE IF NOT EXISTS employees(
                   id integer PRIMARY KEY AUTOINCREMENT,
                   employeename text NOT NULL,
                   email text  UNIQUE NOT NULL,
                   phone text NOT NULL,
                   department text NOT NULL,
                   salary INTEGER NOT NULL,
                   joining TEXT NOT NULL,
                   address Text)
                   """)
    #commit query
    connection.commit()
    #close connection
    connection.close()
#--------SetTheme--------#
@app.route("/set-theme/<theme>")
def set_theme(theme):
    if theme not in["light","dark"]:
       theme="light"
    previous_page=request.referrer or "/"
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
   return render_template("navbar.html")
#-------register(get)-------
@app.route("/registerdemo",methods=["GET"])
def register_page():
    return render_template("registerdemo.html")
@app.route("/registerdemo",methods=["POST"])
def register():
    fullname=request.form["fullname"]
    username=request.form["username"]
    password=request.form["password"]
    
    connection=sqlite3.connect("users.db")
    cursor=connection.cursor()
    cursor.execute("""
        INSERT INTO users(fullname,username,password)
        VALUES(?,?,?)
         """,(fullname,username,password)
         )
    connection.commit()
    connection.close()
    return redirect("/login")


@app.route("/login" ,methods=["GET"]) 
def login_page():
    return render_template("login.html")


@app.route("/login",methods=["POST"])
def login():
    username=request.form["username"]
    password=request.form["password"]
    connection=sqlite3.connect("users.db")
    cursor=connection.cursor()
    cursor.execute("""
         SELECT * FROM users
         WHERE username=? AND password=?
         """,(username,password))
    user=cursor.fetchone()
    connection.cursor()
    if  user:
        return "<h2>login successfull </h2><p>welcome," + username +"! </p>"
    else:  
        return "<h2>login failed </h2><p>username or passwords is incorrect </p>"
#--------Add Employee-----#    
@app.route("/addemployee",methods=["GET"])
def addemployee1():
    return render_template("addemployee.html")     
@app.route("/addemployee",methods=["POST"])
def add_employee_page():
    employeename=request.form["employeename"]
    email=request.form["email"]
    phone=request.form["phone"]
    department=request.form["department"]
    salary=request.form["salary"]
    joining=request.form["joining"]
    address=request.form["address"]
    connection=sqlite3.connect("users.db")
    cursor=connection.cursor()
    cursor.execute("""INSERT INTO employees(
        employeename,
        email,
        phone,
        department,
        salary,
        joining,
        address) VALUES(?,?,?,?,?,?,?)""" 
        ,(employeename,email,phone,department,salary,joining,address))

    connection.commit()
    connection.close()
    return redirect("/employees")
#------Employees----#
@app.route("/employees")
def employees():
  connection=get_database_connection()
  cursor=connection.cursor()
  cursor.execute("""
              SELECT * from employees
              ORDER BY ID ASC
              """)
  employees=cursor.fetchall()
  connection.close()
  return render_template(
    "employees.html",
    employees=employees 
  )
#-----Edit Employee-----#
@app.route("/edit-employee/<int:id>")
def edit_employee_page(id):
    connection=get_database_connection()
    cursor=connection.cursor()
    cursor.execute("""
                 Select * from employees
                 where id=?""",(id,))
    employee=cursor.fetchone()
    connection.cursor()
    if employee is None:
      return """
       <h2>employee not found</h2>
       <a href="/employees>
       Back to employees
       </a>"""
    return render_template(
            "edit-employee.html",
             employee=employee
    )
 #Edit Employee update(post)
@app.route("/edit-employee/<int:id>",methods=["POST"])
def edit_employee(id):
  employeename=request.form["employeename"]
  email=request.form["email"]
  phone=request.form["phone"]
  department=request.form["department"]
  salary=request.form["salary"]
  joining=request.form["joining"]
  address=request.form["address"]
  connection=sqlite3.connect("users.db")
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
#------Delete Employee------#
@app.route("/delete-employee/<int:id>")
def delete_employee(id):
    connection=sqlite3.connect("users.db")
    cursor=connection.cursor()
    cursor.execute("""
              DELETE FROM employees
              WHERE id=?
              """,(id,))
    connection.commit()
    connection.close()
    return redirect("/employees")
#-----Home-----#
@app.route("/home")
def home_page():
    return render_template("home.html")


if __name__=="__main__":
    create_database()
    app.run(debug=True)