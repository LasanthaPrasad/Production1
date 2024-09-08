# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security
from flask_mail import Mail

db = SQLAlchemy()
security = Security()
mail = Mail()