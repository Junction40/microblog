from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__) # Flask application instance
app.config.from_object(Config)
db = SQLAlchemy(app) # Initialising the SQLAlchemy extension with the Flask application
migrate = Migrate(app, db) # Initialising the Flask-Migrate extension with your Flask application and SQLAlchemy instance

from app import routes, models