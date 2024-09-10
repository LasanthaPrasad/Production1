from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.models import ForecastLocation
from app.forecast_providers import SolcastProvider, VisualCrossingProvider
from app import db

def update_forecast_locations():
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
                
                print(f"Updated forecasts for location {location.id}")
            except Exception as e:
                print(f"Error updating forecasts for location {location.id}: {str(e)}")
    
    db.session.commit()
    print("Forecast update complete")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=update_forecast_locations,
        trigger=CronTrigger(hour="*/1"),  # Run every hour
        id="update_forecasts",
        name="Update forecast locations every hour",
        replace_existing=True,
    )
    scheduler.start()