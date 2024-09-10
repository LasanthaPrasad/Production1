import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import current_app
from .forecast_service import ForecastService

logger = logging.getLogger(__name__)

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
        run_date='2023-05-20 00:00:00'  # This date is in the past, so it will run immediately
    )
    
    scheduler.start()
    logger.info("Scheduler started")

def init_app(app):
    with app.app_context():
        start_scheduler()

if __name__ == "__main__":
    start_scheduler()