import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Security, protects against CSRF (Cross-Site Request Forgery) attacks, and ensuring the integrity of cookies
    # When using 'flash' function to show messages or when you hadnles sessions, this key is used to sign the data, ensuring it hasn't been tampared with
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess' 
    
    # Configuration key used by Flask-SQLAlchemy to determine the location of the database
    # Tells SQLAlchemy how to connect to the database (e.g., what type of database to use, where it is located).
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    
    # Email server details for sending errors by email
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
    
    # For pagination
    POSTS_PER_PAGE = 25