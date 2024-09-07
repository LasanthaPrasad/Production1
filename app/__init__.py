from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from flask_security import Security, SQLAlchemyUserDatastore
from .models import User, Role

from .extensions import db, security

from flask_security import SQLAlchemyUserDatastore




db = SQLAlchemy()
scheduler = BackgroundScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    db.init_app(app)
    
    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)




    with app.app_context():
        from . import models
        db.create_all()  # Create tables if they don't exist
        
 #       # Create roles
 #       user_role = user_datastore.find_or_create_role(name='user', description='Regular user')
 #       admin_role = user_datastore.find_or_create_role(name='admin', description='Administrator')
        
        # Create users
 #       if not user_datastore.get_user('praasad@geoclipz.com'):
 #           user_datastore.create_user(email='praasad@geoclipz.com', password='admin', roles=[admin_role])
 #       if not user_datastore.get_user('ee.prasad@gmail.com'):
 #           user_datastore.create_user(email='ee.prasad@gmail.com', password='userq', roles=[user_role])
        



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

