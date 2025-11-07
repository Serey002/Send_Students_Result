import os
from datetime import datetime

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    # Use relative path for database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database/results.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'serey.phem.12022006@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'uqyu sitz mtap aogc'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME') or 'serey.phem.12022006@gmail.com'
    
    # File Upload
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Session Configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour