from flask import Flask

from apscheduler.schedulers.background import BackgroundScheduler
from flask_security import Security, SQLAlchemyUserDatastore
from .models import User, Role

from .extensions import db

from flask_security import SQLAlchemyUserDatastore



from .routes import main as main_blueprint
from flask_mail import Mail




from flask_security import SQLAlchemyUserDatastore
from .extensions import db, security, mail
from .models import User, Role  # Make sure this import is correct









#db = SQLAlchemy()
scheduler = BackgroundScheduler()

#user_datastore = None


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.config['MAIL_SERVER'] = 'smtp.mailgun.org'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'postmaster@sandbox9a55f0d19a734d3b8d7dffb6eacee8e7.mailgun.org'
    app.config['MAIL_PASSWORD'] = 'f9a943428b0cb263bd5f9fb50b2b1bfc-2b755df8-b3abe6d6'
    app.config['SECURITY_EMAIL_SENDER'] = 'sales@geoclipz.com'
    
    db.init_app(app)

    mail.init_app(app)
    
    from .models import User, Role  # Import your User and Role models

    

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)



    with app.app_context():
        from . import models
        db.create_all()  # Create tables if they don't exist
        
 #       # Create roles
        user_role = user_datastore.find_or_create_role(name='user', description='Regular user')
        admin_role = user_datastore.find_or_create_role(name='admin', description='Administrator')
        
        # Create users
        if not user_datastore.get_user('praasad@geoclipz.com'):
            user_datastore.create_user(email='praasad@geoclipz.com', password='admin', roles=[admin_role])
        if not user_datastore.get_user('ee.prasad@gmail.com'):
            user_datastore.create_user(email='ee.prasad@gmail.com', password='userq', roles=[user_role])
        



        from . import solcast_api
        
        # Fetch forecasts on startup
        if solcast_api.fetch_solcast_forecasts():
            print("Initial forecast fetch successful")
        else:
            print("Initial forecast fetch failed")
        
        # Set up scheduler for periodic updates
        scheduler.add_job(func=solcast_api.fetch_solcast_forecasts, trigger="interval", hours=1)
        scheduler.start()
    
    # Import and register blueprints/routes here
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    

    return app

