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