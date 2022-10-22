from flask import Flask, render_template, request, session, redirect, url_for
from dotenv import load_dotenv
import os
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.utils import secure_filename

app = Flask(__name__)

load_dotenv() 

app.secret_key = 'SECRET_KEY'

IMG_FOLDER = os.path.join('static')
app.config['UPLOAD_FOLDER'] = IMG_FOLDER

# Database connection details
app.config['MYSQL_HOST'] = os.getenv('DBHOST')
app.config['MYSQL_PORT'] = int(os.getenv('DBPORT'))
app.config['MYSQL_USER'] = os.getenv('DBUSER')
app.config['MYSQL_PASSWORD'] = os.getenv('DBPASS')
app.config['MYSQL_DB'] = os.getenv('DBNAME')

# Intialize MySQL
mysql = MySQL(app)

@app.route("/")
def index():
    index_photo = 'indexPhoto.jpg'
    return render_template("index.html", image=index_photo)

@app.route("/about/")
def about():
    return render_template("about.html")

@app.route("/employee/")
def employee():
    if 'employeeName' in session:

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customer')
        
        results = cursor.fetchall()

        return render_template("employee.html", employeeName=session['employeeName'], customers=results)

    return redirect(url_for('employee_login'))

@app.route('/employee_login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM employee WHERE username = %s AND password = %s', (username, password,))
        
        employee = cursor.fetchone()

        if employee:
            
            session['employeeName'] = employee['username']

            return redirect(url_for('employee'))

        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

            return render_template("employee_login.html", msg=msg)

    return render_template("employee_login.html")

@app.route('/employee/<int:customerID>')
def view_sessions(customerID):

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM session WHERE customerID = (%s)',(customerID,))
        
    results = cursor.fetchall()

    return render_template('sessions.html', sessions=results, customerID=customerID)

@app.route('/employee/<int:customerID>/customer/<int:sessionID>', methods=['GET', 'POST'])
def update_view(customerID, sessionID):
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO photos (photo_name, customerID, sessionID) VALUES ( %s, %s, %s)', (filename, customerID, sessionID))
        mysql.connection.commit()

        return redirect(url_for('update_view', customerID=customerID, sessionID=sessionID))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM photos Where sessionID = (%s)', (sessionID,))
               
    results = cursor.fetchall()
    images = []

    for photo in results:
        image = photo['photo_name']
        images.append(image)

    return render_template('update.html', images=images, customerID=customerID, sessionID=sessionID)

@app.route("/delete/<filename>")
def delete_view(filename):
    os.remove(os.path.join('static', filename))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM photos Where photo_name = %s', (filename,))
    record = cursor.fetchone()
    customerID = record['customerID']
    sessionID = record['sessionID']

    cursor.execute('Delete From photos Where photo_name = %s', (filename,))
    mysql.connection.commit()

    return redirect(url_for('update_view', customerID=customerID, sessionID=sessionID))

@app.route("/customer/")
def customer():
    if 'customerName' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customer WHERE username = %s', (session['customerName'],))
        customer = cursor.fetchone()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM session WHERE customerID = (%s)',(customer['customerID'],))
        
        results = cursor.fetchall()

        return render_template("customer.html", customerName=session['customerName'], sessions=results, customer=customer)

    return redirect(url_for('customer_login'))

@app.route('/customer_login/', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customer WHERE username = %s AND password = %s', (username, password,))
        
        customer = cursor.fetchone()
        

        if customer:
            
            session['customerName'] = customer['username']

            return redirect(url_for('customer'))

        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

            return render_template("customer_login.html", msg=msg)

    return render_template("customer_login.html")

@app.route('/customer/update/<int:customerID>/', methods=['GET', 'POST'])
def customer_update(customerID):
    if request.method == 'POST':
        email = request.form['email']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE customer SET email = (%s) WHERE customerID = (%s)', (email, customerID))
        mysql.connection.commit()

        return redirect(url_for('customer'))

    return render_template("customer_update.html", customerID=customerID)

@app.route('/logout/')
def logout():
    # remove the username from the session if it's there
    session.pop('customerName', None)
    session.pop('employeeName', None)
    session.pop('loggedin', None)
    session.pop('shoppingCart', None)

    return redirect(url_for('index'))

@app.route('/customer/<int:sessionID>/')
def customer_session(sessionID):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM photos Where sessionID = (%s)', (sessionID,))
               
    results = cursor.fetchall()
    images = []
    price = {"8 x 10": 14.99, "4 x 6": 7.99}

    for photo in results:
        image = photo['photo_name']
        images.append(image)

    return render_template('customer_session.html', images=images, price=price)

@app.route('/customer/add/<filename>/<float:price>/')
def add_to_cart(filename, price):

    if 'shoppingCart' not in session:
        session['shoppingCart'] = []

    if (filename, price) not in session['shoppingCart']:
        session['shoppingCart'].append((filename, price))
        session.modified = True

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM photos Where photo_name = %s', (filename,))
    record = cursor.fetchone()
    sessionID = record['sessionID']    

    return redirect(url_for('customer_session', sessionID=sessionID))

@app.route('/customer/shoppingCart/')
def shopping_cart():

    return render_template('shopping_cart.html')

@app.route('/remove/<filename>/<float:price>/')
def remove(filename, price):
    if (filename, price) in session['shoppingCart']:
        session['shoppingCart'].remove((filename, price))
        session.modified = True
        
    return redirect(url_for('shopping_cart'))

@app.route('/empty_cart/')
def empty():
    session.pop('shoppingCart', None)
    session.modified = True

    return redirect(url_for('shopping_cart'))