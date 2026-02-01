import os
from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
from werkzeug.utils import secure_filename

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    return render_template("index.html", image='indexPhoto.jpg')

@main_bp.route("/about/")
def about():
    return render_template("about.html")

@main_bp.route("/employee/")
def employee():
    if 'employeeName' not in session:
        return redirect(url_for('auth.employee_login'))
    
    results = current_app.customer_repo.get_all_customers()
    return render_template("employee.html", 
                           employeeName=session['employeeName'], 
                           customers=results)

@main_bp.route('/employee/<int:customerID>')
def view_appointments(customerID):
    results = current_app.appointment_repo.get_appointments_by_customerID(customerID)
    return render_template('appointments.html', appointments=results, customerID=customerID)

@main_bp.route('/employee/appointment/<int:appointmentID>', methods=['GET', 'POST'])
def update_view(appointmentID):
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        
        # Using config from current_app for Clean Code
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        
        current_app.photo_repo.save_photo_record(filename, appointmentID)
        return redirect(url_for('main.update_view', appointmentID=appointmentID))

    results = current_app.photo_repo.get_photos_by_appointmentID(appointmentID)
    images = [photo['photo_name'] for photo in results]
    
    return render_template('update.html', images=images, appointmentID=appointmentID)

@main_bp.route("/delete/<filename>")
def delete_view(filename):
    # Logic moved from app.py
    photo = current_app.photo_repo.get_photo_by_name(filename)
    appointmentID = photo['appointmentID']
    
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        
    current_app.photo_repo.delete_photo_record(filename)
    return redirect(url_for('main.update_view', appointmentID=appointmentID))

# ... Add your /customer/ and shopping cart routes here following the same pattern ...

@main_bp.route('/customer/')
def customer():
    if 'customerName' in session:
        customer  = current_app.customer_repo.get_customer_by_name(session['customerName'])
        results = current_app.appointment_repo.get_appointments_by_customerID(customer['customerID'])

        return render_template("customer.html", customerName=session['customerName'], appointments=results, customer=customer)

    return redirect(url_for('auth.customer_login'))

@main_bp.route('/customer/update/<int:customerID>/', methods=['GET', 'POST'])
def customer_update(customerID):
    if request.method == 'POST':
        email = request.form['email']

        current_app.customer_repo.set_customer_email(email, customerID)

        return redirect(url_for('main.customer'))

    return render_template("customer_update.html", customerID=customerID)

@main_bp.route('/customer/<int:appointmentID>/')
def customer_appointment(appointmentID):
    results = current_app.photo_repo.get_photos_by_appointmentID(appointmentID)
    images = []
    price = {"8 x 10": 14.99, "4 x 6": 7.99}

    for photo in results:
        image = photo['photo_name']
        images.append(image)

    return render_template('customer_appointment.html', images=images, price=price)

@main_bp.route('/customer/add/<filename>/<float:price>/')
def add_to_cart(filename, price):

    if 'shoppingCart' not in session:
        session['shoppingCart'] = []

    if (filename, price) not in session['shoppingCart']:
        session['shoppingCart'].append((filename, price))
        session.modified = True

    record = current_app.photo_repo.get_photo_by_name(filename)
    appointmentID = record['appointmentID']

    return redirect(url_for('main.customer_appointment', appointmentID=appointmentID))

@main_bp.route('/customer/shoppingCart/')
def shopping_cart():

    return render_template('shopping_cart.html')

@main_bp.route('/remove/<filename>/<float:price>/')
def remove(filename, price):
    if (filename, price) in session['shoppingCart']:
        session['shoppingCart'].remove((filename, price))
        session.modified = True

    return redirect(url_for('main.shopping_cart'))

@main_bp.route('/empty_cart/')
def empty():
    session.pop('shoppingCart', None)
    session.modified = True

    return redirect(url_for('main.shopping_cart'))
