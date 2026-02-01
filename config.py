# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-key-for-dev')
    UPLOAD_FOLDER = os.path.join('static')
    
    # Database Settings
    MYSQL_HOST = os.getenv('DBHOST')
    MYSQL_PORT = int(os.getenv('DBPORT', 3306))
    MYSQL_USER = os.getenv('DBUSER')
    MYSQL_PASSWORD = os.getenv('DBPASS')
    MYSQL_DB = os.getenv('DBNAME')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    # In production, you might have different DB settings

