import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import current_app
from .forecast_service import ForecastService
from datetime import datetime

#logger = logging.getLogger(__name__)



from .forecast_service import ForecastService

def update_forecast_locations():
    print("update_forecast_locations function called")
    forecast_service = ForecastService()
    forecast_service.update_forecasts()

def start_scheduler():
    print("start_scheduler function called")
    scheduler = BackgroundScheduler()
    
    scheduler.add_job(
        func=update_forecast_locations,
        trigger=CronTrigger(hour="*/1"),
        id="update_forecasts",
        name="Update forecast locations every hour",
        replace_existing=True,
    )
    
    # Run immediately when the scheduler starts
    scheduler.add_job(
        func=update_forecast_locations,
        trigger='date',
        run_date=datetime.now(),
        id="initial_update",
        name="Initial forecast update",
    )
    
    scheduler.start()
    print("Scheduler started")

# Call this function to start the scheduler immediately
update_forecast_locations()



