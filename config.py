import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Database
    DATABASE_PATH = 'database/students.db'
    
    # File Upload
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    
    # Email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('serey.phem.12022006@gmail.com')
    MAIL_PASSWORD = os.getenv('akry zpee ztai jrnh')
    MAIL_DEFAULT_SENDER = os.getenv('serey.phem.12022006@gmail.com', MAIL_USERNAME)
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Features
    BATCH_SIZE = 50  # Emails per batch
    RATE_LIMIT = 100  # Emails per hour