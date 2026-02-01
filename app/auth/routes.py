from flask import Blueprint, render_template, request, session, redirect, url_for, current_app

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/employee_login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        employee = current_app.employee_repo.get_by_credentials(username, password)

        if employee:
            session['employeeName'] = employee['username']
            return redirect(url_for('main.employee')) # 'main' is the other blueprint
        
        return render_template("employee_login.html", msg='Incorrect username/password!')

    return render_template("employee_login.html")

@auth_bp.route('/customer_login/', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        customer = current_app.customer_repo.get_by_credentials(username, password)

        if customer:
            session['customerName'] = customer['username']
            return redirect(url_for('main.customer'))
        
        return render_template("customer_login.html", msg='Incorrect username/password!')

    return render_template("customer_login.html")

@auth_bp.route('/logout/')
def logout():
    session.clear() 
    return redirect(url_for('main.index'))

