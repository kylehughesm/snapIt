# mysql_repository.py

from .repositories import CustomerRepository, EmployeeRepository, PhotoRepository, AppointmentRepository
import MySQLdb.cursors

class MySQLCustomerRepository(CustomerRepository):
    def __init__(self, mysql_instance):
        self.mysql = mysql_instance

    def get_by_credentials(self, username, password):
        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customer WHERE username = %s AND password = %s', (username, password))
        return cursor.fetchone()

    def get_all_customers(self):
        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customer')
        return cursor.fetchall()

    def get_customer_by_name(self, customerID):
        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customer WHERE username = %s', (customerID))
        return cursor.fetchone()

    def set_customer_email(self, email, customerID):
        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE customer SET email = (%s) WHERE customerID = (%s)', (email, customerID))
        self.mysql.connection.commit()        

class MySQLPhotoRepository(PhotoRepository):
    def __init__(self, mysql_instance):
        self.mysql = mysql_instance

    def save_photo_record(self, filename, appointmentID): 
        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO photos (photo_name, appointmentID) VALUES ( %s, %s)', (filename, appointmentID))
        self.mysql.connection.commit()

    def delete_photo_record(self, filename):
        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)        
        cursor.execute('Delete From photos Where photo_name = %s', (filename,))
        self.mysql.connection.commit()        

    def get_photo_by_name(self, filename):
        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM photos Where photo_name = %s', (filename,))
        return cursor.fetchone()

    def get_photos_by_appointmentID(self, appointmentID):
        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM photos Where appointmentID = (%s)', (appointmentID,))
        return cursor.fetchall()

class MySQLAppointmentRepository(AppointmentRepository):
    def __init__(self, mysql_instance):
        self.mysql = mysql_instance

    def get_appointments_by_customerID(self, customerID):
        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM appointment WHERE customerID = (%s)',(customerID,))
        return cursor.fetchall()
    

class MySQLEmployeeRepository(EmployeeRepository):
    def __init__(self, mysql_instance):
        self.mysql = mysql_instance

    def get_by_credentials(self, username, password): 
        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM employee WHERE username = %s AND password = %s', (username, password,))
        return  cursor.fetchone()
