from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Initialize SQLAlchemy without binding it to an app yet
db = SQLAlchemy()

# Create scheduler
scheduler = BackgroundScheduler()

# Create the SQLAlchemy engine
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

# Create a sessionmaker
Session = sessionmaker(bind=engine)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize SQLAlchemy with the app
    db.init_app(app)

    # Import and register blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Initialize scheduler jobs
    with app.app_context():
        from app.utils import fetch_solar_forecast, fetch_wind_forecast, fetch_hydro_forecast
        scheduler.add_job(fetch_solar_forecast, 'interval', hours=1)
        scheduler.add_job(fetch_wind_forecast, 'interval', hours=1)
        scheduler.add_job(fetch_hydro_forecast, 'interval', hours=1)

    # Start the scheduler
    scheduler.start()


    return app

# Make sure these are accessible when imported from app
__all__ = ['create_app', 'db', 'Session', 'engine', 'scheduler']