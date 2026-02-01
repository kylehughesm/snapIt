from flask import Flask
from flask_mysqldb import MySQL
from config import Config
from .repositories.mysql_repo import (
    MySQLCustomerRepository, 
    MySQLEmployeeRepository, 
    MySQLPhotoRepository, 
    MySQLAppointmentRepository
)

# 1. Initialize extension globally
mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 2. Initialize mysql with app context
    mysql.init_app(app)

    # 3. Attach Repositories to the app instance
    with app.app_context():
        app.customer_repo = MySQLCustomerRepository(mysql)
        app.employee_repo = MySQLEmployeeRepository(mysql)
        app.photo_repo = MySQLPhotoRepository(mysql)
        app.appointment_repo = MySQLAppointmentRepository(mysql)

    # 4. Register Blueprints
    from .auth.routes import auth_bp
    from .main.routes import main_bp # Assuming you move the rest to main/routes.py
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app

