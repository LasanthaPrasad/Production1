import logging
from logging.handlers import RotatingFileHandler
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import current_app
from .forecast_service import ForecastService

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
        forecast_service = ForecastService()
        try:
            forecast_service.update_forecasts()
            logger.info("Forecast update process completed successfully")
        except Exception as e:
            logger.error(f"Error in forecast update process: {str(e)}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    
    # Schedule the job to run every hour
    scheduler.add_job(
        func=update_forecast_locations,
        trigger=CronTrigger(hour="*/1"),  # Run every hour
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
        run_date='2024-09-11 00:00:00'  # This date is in the past, so it will run immediately
    )
    
    scheduler.start()
    logger.info("Scheduler started")

def init_app(app):
    with app.app_context():
        start_scheduler()