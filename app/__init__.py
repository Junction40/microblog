from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__) # Flask application instance
app.config.from_object(Config)
db = SQLAlchemy(app) # Initialising the SQLAlchemy extension with the Flask application
migrate = Migrate(app, db) # Initialising the Flask-Migrate extension with your Flask application and SQLAlchemy instance
login = LoginManager(app) # Initialising the login manager right after the application instance
login.login_view = 'login' # 'login' is the fu nction (or endpoint) name for the login vieew

from app import routes, models