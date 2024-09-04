from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler

db = SQLAlchemy()
scheduler = BackgroundScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    db.init_app(app)
    
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
    
    # Import and register blueprints/routes here
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app