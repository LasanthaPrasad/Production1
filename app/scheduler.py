import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import current_app
from .forecast_service import ForecastService

scheduler = BlockingScheduler()

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

@scheduler.scheduled_job('cron', hour='*')  # Run every hour
def scheduled_job():
    update_forecast_locations()

def init_scheduler():
    logger.info("Initializing scheduler")
    scheduler.start()

if __name__ == "__main__":
    init_scheduler()