from flask import Flask, render_template, request, session, redirect, url_for
import os
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from config import Config
from .repositories.mysql_repo import MySQLCustomerRepository, MySQLEmployeeRepository, MySQLPhotoRepository, MySQLAppointmentRepository


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mysql = MySQL(app)

    customer_repo = MySQLCustomerRepository(mysql)
    employee_repo = MySQLEmployeeRepository(mysql)
    photo_repo = MySQLPhotoRepository(mysql)
    appointment_repo = MySQLAppointmentRepository(mysql)

    mysql.init_app(app)


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

            results = customer_repo.get_all_customers() 

            return render_template("employee.html", employeeName=session['employeeName'], customers=results)

        return redirect(url_for('employee_login'))

    @app.route('/employee_login', methods=['GET', 'POST'])
    def employee_login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            employee = employee_repo.get_by_credentials(username, password) 

            if employee:

                session['employeeName'] = employee['username']

                return redirect(url_for('employee'))

            else:
                # Account doesnt exist or username/password incorrect
                msg = 'Incorrect username/password!'

                return render_template("employee_login.html", msg=msg)

        return render_template("employee_login.html")

    @app.route('/employee/<int:customerID>')
    def view_appointments(customerID):


        results = appointment_repo.get_appointments_by_customerID(customerID)

        return render_template('appointments.html', appointments=results)

    @app.route('/employee/appointment/<int:appointmentID>', methods=['GET', 'POST'])
    def update_view( appointmentID):
        if request.method == 'POST':
            file = request.files['file']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            photo_repo.save_photo_record(filename, appointmentID)

            return redirect(url_for('update_view', appointmentID=appointmentID))

        results = photo_repo.get_photos_by_appointmentID(appointmentID)

        images = []

        for photo in results:
            image = photo['photo_name']
            images.append(image)

        return render_template('update.html', images=images, appointmentID=appointmentID)

    @app.route("/delete/<filename>")
    def delete_view(filename):
        os.remove(os.path.join('static', filename))
        photo= photo_repo.get_photo_by_name(filename) 
        appointmentID = photo['appointmentID']

        photo_repo.delete_photo_record(filename)

        return redirect(url_for('update_view', appointmentID=appointmentID))

    @app.route('/customer/')
    def customer():
        if 'customerName' in session:
            customer  = customer_repo.get_customer_by_name(session['customerName'])
            results = appointment_repo.get_appointments_by_customerID(customer['customerID'])

            return render_template("customer.html", customerName=session['customerName'], appointments=results, customer=customer)

        return redirect(url_for('customer_login'))

    @app.route('/customer_login/', methods=['GET', 'POST'])
    def customer_login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            customer = customer_repo.get_by_credentials(username, password)


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

            customer_repo.set_customer_email(email, customerID)

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

    @app.route('/customer/<int:appointmentID>/')
    def customer_appointment(appointmentID):
        results = photo_repo.get_photos_by_appointmentID(appointmentID)
        images = []
        price = {"8 x 10": 14.99, "4 x 6": 7.99}

        for photo in results:
            image = photo['photo_name']
            images.append(image)

        return render_template('customer_appointment.html', images=images, price=price)

    @app.route('/customer/add/<filename>/<float:price>/')
    def add_to_cart(filename, price):

        if 'shoppingCart' not in session:
            session['shoppingCart'] = []

        if (filename, price) not in session['shoppingCart']:
            session['shoppingCart'].append((filename, price))
            session.modified = True

        record = photo_repo.get_photo_by_name(filename)
        appointmentID = record['appointmentID']

        return redirect(url_for('customer_appointment', appointmentID=appointmentID))

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

    return app
