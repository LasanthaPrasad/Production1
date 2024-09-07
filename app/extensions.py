from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager  # Note the capital 'L' and 'M'

db = SQLAlchemy()
login_manager = LoginManager()  # This should be lowercase
login_manager.login_view = 'auth.login'