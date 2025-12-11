from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'csc206cars'

mysql = MySQL(app)

@app.route('/')

#Code for login and logout was found here https://www.geeksforgeeks.org/python/login-and-registration-project-using-flask-and-mysql/
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['userID'] = account['userID']
            session['username'] = account['username']
            session['role'] = account['role']
            session['first_name'] = account['first_name']
            session['last_name'] = account['last_name']
            return render_template('home.html', msg='Logged in successfully!')
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userID', None)
    session.pop('username', None)
    session.pop('role', None)
    session.pop('first_name', None)
    session.pop('last_name', None)
    return redirect(url_for('login'))

@app.route('/home')
def home():
    return render_template("home.html", home=home)

@app.route('/vehicles')
def cars():

    #The request.args.get was found here https://www.geeksforgeeks.org/python/using-request-args-for-a-variable-url-in-flask/
    vehicle_type = request.args.get('vehicle_type', '')
    manufacturer = request.args.get('manufacturer', '')
    model_year = request.args.get('model_year', '')
    fuel_type = request.args.get('fuel_type', '')
    color = request.args.get('color', '')

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    #GROUP_CONCAT was found here https://www.geeksforgeeks.org/sql/mysql-group_concat-function
    #DISTINCT was found here https://www.w3schools.com/sql/sql_distinct.asp
    #SEPARATOR was found here https://www.geeksforgeeks.org/sql/mysql-group_concat-function
    #COALESCE was found here https://www.w3schools.com/sql/func_mysql_coalesce.asp
    sql = """SELECT v.vehicleID, v.vin, v.model_year, v.model_name, vt.vehicle_type_name, m.manufacturer_name,
    GROUP_CONCAT(DISTINCT c.color_name SEPARATOR ', ') AS colors, pt.purchase_price,
    (1.4 * COALESCE(pt.purchase_price, 0) + 1.2 * COALESCE(SUM(p.cost * p.quantity), 0)) AS price
    FROM vehicles v
    LEFT JOIN vehicletypes vt ON v.vehicle_typeID = vt.vehicle_typeID
    LEFT JOIN manufacturers m ON v.manufacturerID = m.manufacturerID
    LEFT JOIN vehiclecolors vc ON vc.vehicleID = v.vehicleID
    LEFT JOIN colors c ON vc.colorID = c.colorID
    LEFT JOIN purchasetransactions pt ON pt.vehicleID = v.vehicleID
    LEFT JOIN partorders po ON po.vehicleID = v.vehicleID
    LEFT JOIN parts p ON p.part_orderID = po.part_orderID
    LEFT JOIN salestransactions s ON s.vehicleID = v.vehicleID
    WHERE s.sales_transactionID IS NULL AND NOT EXISTS 
        (SELECT 1 FROM partorders po JOIN parts p ON p.part_orderID = po.part_orderID WHERE po.vehicleID = v.vehicleID AND p.status <> 'Installed')"""
    
    #The AND, LIKE, and % were found here https://www.w3schools.com/mysql/mysql_wildcards.asp
    #  
    if vehicle_type != "": 
        sql += " AND vt.vehicle_type_name LIKE '%" + vehicle_type + "%'" 

    if manufacturer != "": 
        sql += " AND m.manufacturer_name LIKE '%" + manufacturer + "%'" 

    if model_year != "": 
        sql += " AND v.model_year LIKE '%" + model_year + "%'"

    if fuel_type != "":
        sql += " AND v.fuel_type LIKE '%" + fuel_type + "%'" 

    if color != "": 
        sql += " AND c.color_name LIKE '%" + color + "%'"

    sql += " GROUP BY v.vehicleID ORDER BY v.model_year DESC, m.manufacturer_name ASC"

    cur.execute(sql)
    vehicles = cur.fetchall()
    cur.close()

    #The render_template was found here https://www.geeksforgeeks.org/python/flask-rendering-templates

    return render_template("vehicles.html", vehicles=vehicles)

@app.route('/allcars')
def allcars():

    vehicle_type = request.args.get('vehicle_type', '')
    manufacturer = request.args.get('manufacturer', '')
    model_year = request.args.get('model_year', '')
    fuel_type = request.args.get('fuel_type', '')
    color = request.args.get('color', '')

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    sql = """SELECT v.vehicleID, v.vin, v.model_year, v.model_name, vt.vehicle_type_name, m.manufacturer_name,
    GROUP_CONCAT(DISTINCT c.color_name SEPARATOR ', ') AS colors, pt.purchase_price,
    (1.4 * COALESCE(pt.purchase_price, 0) + 1.2 * COALESCE(SUM(p.cost * p.quantity), 0)) AS price,
    CASE WHEN s.sales_transactionID IS NULL THEN 0 ELSE 1 END AS bought
    FROM vehicles v
    LEFT JOIN vehicletypes vt ON v.vehicle_typeID = vt.vehicle_typeID
    LEFT JOIN manufacturers m ON v.manufacturerID = m.manufacturerID
    LEFT JOIN vehiclecolors vc ON vc.vehicleID = v.vehicleID
    LEFT JOIN colors c ON vc.colorID = c.colorID
    LEFT JOIN purchasetransactions pt ON pt.vehicleID = v.vehicleID
    LEFT JOIN partorders po ON po.vehicleID = v.vehicleID
    LEFT JOIN parts p ON p.part_orderID = po.part_orderID
    LEFT JOIN salestransactions s ON s.vehicleID = v.vehicleID
    WHERE 1=1"""

    #WHERE 1=1 was found here https://www.w3schools.com/sql/sql_injection.asp

    if vehicle_type != "": 
        sql += " AND vt.vehicle_type_name LIKE '%" + vehicle_type + "%'" 

    if manufacturer != "": 
        sql += " AND m.manufacturer_name LIKE '%" + manufacturer + "%'" 

    if model_year != "": 
        sql += " AND v.model_year LIKE '%" + model_year + "%'"

    if fuel_type != "":
        sql += " AND v.fuel_type LIKE '%" + fuel_type + "%'" 

    if color != "": 
        sql += " AND c.color_name LIKE '%" + color + "%'"

    sql += " GROUP BY v.vehicleID ORDER BY v.model_year DESC, m.manufacturer_name ASC"

    cur.execute(sql)
    cars = cur.fetchall()
    cur.close()

    return render_template("vehicles.html", cars=cars)

#The <> or was found here https://www.geeksforgeeks.org/python/generating-dynamic-urls-in-flask
@app.route('/vehicles/<vin>')
def details(vin):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    detail = """SELECT v.*, vt.vehicle_type_name, m.manufacturer_name,
    GROUP_CONCAT(DISTINCT c.color_name SEPARATOR ', ') AS colors, pt.purchase_price,
    (1.4 * COALESCE(pt.purchase_price, 0) + 1.2 * COALESCE(SUM(p.cost * p.quantity), 0)) AS price
    FROM vehicles v
    LEFT JOIN vehicletypes vt ON v.vehicle_typeID = vt.vehicle_typeID
    LEFT JOIN manufacturers m ON v.manufacturerID = m.manufacturerID
    LEFT JOIN vehiclecolors vc ON vc.vehicleID = v.vehicleID
    LEFT JOIN colors c ON vc.colorID = c.colorID
    LEFT JOIN purchasetransactions pt ON pt.vehicleID = v.vehicleID
    LEFT JOIN partorders po ON po.vehicleID = v.vehicleID
    LEFT JOIN parts p ON p.part_orderID = po.part_orderID
    WHERE v.vin = %s
    GROUP BY v.vehicleID"""
    
    #The %s was found here https://www.w3schools.com/sql/sql_wildcards.asp and here https://www.drupal.org/forum/support/module-development-and-code-questions/2007-03-16/d-and-s-in-sql-queries
    #%s is a placeholder for a string and will be replaced by the vin that populates it
    cur.execute(detail, (vin,))

    #fetchone was found here https://www.geeksforgeeks.org/dbms/querying-data-from-a-database-using-fetchone-and-fetchall
    vehicle = cur.fetchone()

    part = """SELECT p.*
    FROM partorders po
    JOIN parts p ON p.part_orderID = po.part_orderID
    JOIN vehicles v ON v.vehicleID = po.vehicleID
    WHERE v.vin = %s"""

    cur.execute(part, (vin,))
    parts = cur.fetchall()

    sell_car = """SELECT * FROM customers c
    JOIN salestransactions s ON s.customerID = c.customerID
    JOIN vehicles v ON v.vehicleID = s.vehicleID
    WHERE v.vin = %s"""
    
    cur.execute(sell_car, (vin,))
    seller = cur.fetchone()

    buy = """SELECT * FROM customers c
    JOIN purchasetransactions p ON p.customerID = c.customerID
    JOIN vehicles v ON v.vehicleID = p.vehicleID
    WHERE v.vin = %s"""
    
    cur.execute(buy, (vin,))
    buyer = cur.fetchone()
    cur.close()

    return render_template("vehicle_details.html", vehicle=vehicle, parts=parts, seller=seller, buyer=buyer)  

@app.route('/mark_installed/<partID>/<vin>')
def mark(partID, vin):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    #Update was found here https://www.w3schools.com/sql/sql_update.asp
    sql = "UPDATE parts SET status='Installed' WHERE partID=%s"

    cur.execute(sql, (partID,))
    mysql.connection.commit()
    cur.close()

    return render_template("vehicle_details.html", vin=vin)

@app.route('/newcustomer', methods=['GET','POST'])
def new():
    msg = ''

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone_number = request.form['phone_number']
        email_address = request.form['email_address']
        street = request.form['street']
        city = request.form['city']
        state = request.form['state']
        postal_code = request.form['postal_code']
        id_number = request.form['id_number']
        business_name = request.form['business_name']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        sql = """INSERT INTO customers (phone_number, email_address, street, city, state, postal_code, id_number, first_name, last_name, business_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        cur.execute(sql, (phone_number, email_address, street, city, state, postal_code, id_number, first_name, last_name, business_name))

        mysql.connection.commit()

        new_id = cur.lastrowid

        cur.close()

        return redirect(url_for('cars'))

    return render_template("newcustomer.html", customerID=new_id)

@app.route('/sellcar/<vin>')
def sell(vin):
    customerID = request.args.get('customerID', '')

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    sql = "SELECT * FROM vehicles WHERE vin = %s"
    cur.execute(sql, (vin,))
    vehicle = cur.fetchone()

    cur.execute("SELECT * FROM customers ORDER BY last_name ASC")
    customers = cur.fetchall()
    cur.close()

    return render_template("sellcar.html", customerID=customerID, customers=customers, vehicle=vehicle)

@app.route('/sold', methods=['POST'])
def sold():
    if request.method == 'POST':
        vehicleID = request.form['vehicleID']
        customerID = request.form['customerID']
        userID = session['userID']
        sales_date = request.form['sales_date']

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    sql = """INSERT INTO salestransactions (vehicleID, userID, customerID, sales_date)
    VALUES (%s, %s, %s, %s)"""

    cur.execute(sql, (vehicleID, customerID, userID, sales_date))
    cur.close()

    return redirect(url_for('cars'))

@app.route('/buycar/<vin>')
def buy(vin):
    customerID = request.args.get('customerID', '')

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)\
    
    sql = "SELECT * FROM vehicles WHERE vin = %s"
    cur.execute(sql, (vin,))
    vehicle = cur.fetchone()

    sell = """SELECT * FROM customers c
    JOIN purchasetransactions p ON p.customerID = c.customerID
    JOIN vehicles v ON v.vehicleID = p.vehicleID
    WHERE v.vin = %s"""

    cur.execute(sell, (vin,))
    seller = cur.fetchone()
    cur.close()
    return render_template("buycar.html", customerID=customerID, seller=seller, vehicle=vehicle)

@app.route('/purchase_vehicle', methods=['POST'])
def purchase():
    vehicleID = request.form['vehicleID']
    customerID = request.form['customerID']
    userID = session['userID']
    purchase_date = request.form['purchase_date']
    purchase_price = request.form['purchase_price']
    vehicle_condition = request.form['vehicle_condition']

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    sql = """INSERT INTO purchasetransactions (vehicleID, userID, customerID, purchase_price, purchase_date, vehicle_condition)
    VALUES (%s, %s, %s, %s, %s, %s)"""

    cur.execute(sql, (vehicleID, userID, customerID, purchase_price, purchase_date, vehicle_condition))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('cars'))


@app.route('/profile')
def profile():
    return render_template("profile.html", profile=profile)

@app.route('/reports')
def reports():
    return render_template('reports.html', reports=reports)

@app.route('/sales_productivity')
def sales_productivity():

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    sql = """SELECT u.username, COUNT(s.sales_transactionID) AS vehicles_sold,
    SUM(1.4 * pt.purchase_price + 1.2 * COALESCE(parts_sum.total_cost)) AS total,
    AVG(1.4 * pt.purchase_price + 1.2 * COALESCE(parts_sum.total_cost)) AS average_price
    FROM salestransactions s
    JOIN users u ON s.userID = u.userID
    LEFT JOIN purchasetransactions pt ON pt.vehicleID = s.vehicleID
    LEFT JOIN (SELECT po.vehicleID, SUM(p.cost * p.quantity) AS total_cost
    FROM partorders po
    JOIN parts p ON p.part_orderID = po.part_orderID
    GROUP BY po.vehicleID) parts_sum ON parts_sum.vehicleID = s.vehicleID
    GROUP BY u.userID
    ORDER BY vehicles_sold DESC, total DESC"""

    cur.execute(sql)
    sales = cur.fetchall()
    cur.close()

    return render_template("sales_productivity.html", sales=sales)

@app.route('/seller-history')
def seller_history():

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    sql = """SELECT c.first_name, c.last_name,
    COUNT(pt.purchase_transactionID) AS sold,
    SUM(pt.purchase_price) AS total
    FROM customers c
    LEFT JOIN purchasetransactions pt ON pt.customerID = c.customerID
    GROUP BY c.customerID
    ORDER BY sold DESC, total ASC"""

    cur.execute(sql)
    sellers = cur.fetchall()
    cur.close()

    return render_template("seller_history.html", sellers=sellers)

@app.route('/part_statistics')
def part_statistics():

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    sql = """SELECT v.vendor_name, COALESCE(SUM(p.quantity), 0) AS parts,
    COALESCE(SUM(p.cost * p.quantity), 0) AS total,
    COALESCE(AVG(p.cost), 0) AS average_cost
    FROM vendors v
    LEFT JOIN partorders po ON po.vendorID = v.vendorID
    LEFT JOIN parts p ON p.part_orderID = po.part_orderID
    GROUP BY v.vendorID
    ORDER BY parts DESC"""

    cur.execute(sql)
    parts = cur.fetchall()
    cur.close()

    return render_template("part_statistics.html", parts=parts)

if __name__ == "__main__":
    app.run(debug=True)