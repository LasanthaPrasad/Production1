from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db = SQLAlchemy()
scheduler = BackgroundScheduler()

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Initialize scheduler jobs
    with app.app_context():
        from app.utils import fetch_solar_forecast, fetch_wind_forecast, fetch_hydro_forecast
        
        # Pass app as an argument to these functions
        scheduler.add_job(fetch_solar_forecast, 'interval', hours=1, args=[app])
        scheduler.add_job(fetch_wind_forecast, 'interval', hours=1, args=[app])
        scheduler.add_job(fetch_hydro_forecast, 'interval', hours=1, args=[app])

    scheduler.start()

    return app

__all__ = ['create_app', 'db', 'Session', 'engine', 'scheduler']