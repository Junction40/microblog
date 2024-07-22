from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
import logging
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
from flask_moment import Moment
from flask_babel import Babel
import os


def get_locale():
    # accept_languages is an attribute of Flask's request object 
    # accept_languages header specifies the client language and locale preferences as a weighted list
    # return 'es' to try spanish
    return request.accept_languages.best_match(app.config['LANGUAGES'])
app = Flask(__name__) # Flask application instance
app.config.from_object(Config)
db = SQLAlchemy(app) # Initialising the SQLAlchemy extension with the Flask application
migrate = Migrate(app, db) # Initialising the Flask-Migrate extension with your Flask application and SQLAlchemy instance
login = LoginManager(app) # Initialising the login manager right after the application instance
login.login_view = 'login' # 'login' is the fu nction (or endpoint) name for the login view
mail = Mail(app) # Flask mail for sending emails / pyjwt to generate secture tokens (JSON Web Tokens) for password reset links
moment = Moment(app) # JS library that convertsfrom UTC to local timezone in the browser, using JavaScript (works together with moment.js)
babel = Babel(app, locale_selector=get_locale) # Babel instance initialised a locale_selector, which is set to the get_locale function invoked on each request

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
    
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')


from app import routes, models, errors