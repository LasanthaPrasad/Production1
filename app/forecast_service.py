from .forecast_providers import SolcastProvider, VisualCrossingProvider
from .models import ForecastLocation, IrradiationForecast
from . import db
import logging

logger = logging.getLogger(__name__)

class ForecastService:
    def __init__(self):
        self.providers = {
            'solcast': SolcastProvider(),
            'visualcrossing': VisualCrossingProvider(),
        }

    def fetch_forecasts(self, location):
        provider = self.providers.get(location.provider_name.lower())
        if not provider:
            raise ValueError(f"Unsupported provider: {location.provider_name}")

        data = provider.fetch_forecast(location)
        forecasts = provider.parse_forecast(data)
        return forecasts

    def update_forecasts(self):
        locations = ForecastLocation.query.all()
        for location in locations:
            try:
                logger.info(f"Fetching forecasts for location {location.id} ({location.provider_name})")
                forecasts = self.fetch_forecasts(location)
                
                # Clear existing forecasts for this location
                IrradiationForecast.query.filter_by(forecast_location_id=location.id).delete()
                
                # Add new forecasts
                for forecast in forecasts:
                    forecast.forecast_location_id = location.id
                    db.session.add(forecast)
                
                db.session.commit()
                logger.info(f"Updated forecasts for location {location.id}")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error updating forecasts for location {location.id}: {str(e)}")
        
        logger.info("Forecast update complete")