import logging
from logging.handlers import RotatingFileHandler
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.models import ForecastLocation
from app.forecast_providers import SolcastProvider, VisualCrossingProvider
from app import db
from flask import current_app

# Set up logging
logger = logging.getLogger('forecast_updater')
logger.setLevel(logging.INFO)

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.mkdir('logs')

# Create a rotating file handler
file_handler = RotatingFileHandler('logs/forecast_updates.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

def update_forecast_locations():
    with current_app.app_context():
        logger.info("Starting forecast update process")
        locations = ForecastLocation.query.all()
        providers = {
            'solcast': SolcastProvider(),
            'visualcrossing': VisualCrossingProvider(),
            # Add other providers here as needed
        }

        for location in locations:
            provider = providers.get(location.provider_name.lower())
            if provider:
                try:
                    data = provider.fetch_forecast(location)
                    forecasts = provider.parse_forecast(data)
                    
                    # Clear existing forecasts for this location
                    location.irradiation_forecasts.delete()
                    
                    # Add new forecasts
                    for forecast in forecasts:
                        forecast.forecast_location_id = location.id
                        db.session.add(forecast)
                    
                    logger.info(f"Updated forecasts for location {location.id} ({location.provider_name})")
                except Exception as e:
                    logger.error(f"Error updating forecasts for location {location.id} ({location.provider_name}): {str(e)}")
        
        db.session.commit()
        logger.info("Forecast update process completed")

def start_scheduler():
    scheduler = BackgroundScheduler()
    
    # Schedule the job to run every hour
    scheduler.add_job(
        func=update_forecast_locations,
        trigger=CronTrigger(hour="*/1"),
        id="update_forecasts",
        name="Update forecast locations every hour",
        replace_existing=True,
    )
    
    # Run the job immediately when the scheduler starts
    scheduler.add_job(
        func=update_forecast_locations,
        trigger='date',
        id="initial_update",
        name="Initial forecast update",
        run_date='2023-05-20 00:00:00'  # This date is in the past, so it will run immediately
    )
    
    scheduler.start()
    logger.info("Scheduler started")