# repositories.py
from abc import ABC, abstractmethod

class CustomerRepository(ABC):
    @abstractmethod
    def get_by_credentials(self, username, password): pass
    
    @abstractmethod
    def get_all_customers(self): pass

    @abstractmethod
    def get_customer_by_name(self, customerID): pass

    @abstractmethod
    def set_customer_email(self, email, customerID): pass

class PhotoRepository(ABC):
    @abstractmethod
    def save_photo_record(self, filename, appointmentID): pass
    
    @abstractmethod
    def delete_photo_record(self, filename): pass

    @abstractmethod
    def get_photo_by_name(self, filename): pass

    @abstractmethod
    def get_photos_by_appointmentID(self, appointmentID): pass

class AppointmentRepository(ABC):
    @abstractmethod
    def get_appointments_by_customerID(self, customerID): pass

class EmployeeRepository(ABC):
    @abstractmethod
    def get_by_credentials(self, username, password): pass
