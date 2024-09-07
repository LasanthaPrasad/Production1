from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from flask_login import loginManager
from flask_principal import Principal, Permission, RoleNeed
from app.models import User
from config import Config

db = SQLAlchemy()
scheduler = BackgroundScheduler()




def create_app():
    app = Flask(__name__)
    app.config.from_object('Config')
    
    db.init_app(app)
    

    login_manager.init_app(app)




    with app.app_context():
        from . import models
        db.create_all()  # Create tables if they don't exist
        
        from . import solcast_api
        
        # Fetch forecasts on startup
        if solcast_api.fetch_solcast_forecasts():
            print("Initial forecast fetch successful")
        else:
            print("Initial forecast fetch failed")
        
        # Set up scheduler for periodic updates
        scheduler.add_job(func=solcast_api.fetch_solcast_forecasts, trigger="interval", hours=1)
        scheduler.start()
    

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)



    
   
    return app
