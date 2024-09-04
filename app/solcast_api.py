import requests
from app import db
from app.models import ForecastLocation, Forecast
from datetime import datetime
import os

SOLCAST_API_KEY = os.environ.get('SOLCAST_API_KEY')

def fetch_solcast_data():
    locations = ForecastLocation.query.all()
    for location in locations:
        url = f"https://api.solcast.com.au/world_radiation/forecasts?latitude={location.latitude}&longitude={location.longitude}&api_key={SOLCAST_API_KEY}&format=json"
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            # Process and store the forecast data
            for forecast in data['forecasts']:
                new_forecast = Forecast(
                    forecast_location_id=location.id,
                    forecast_timestamp=datetime.fromisoformat(forecast['period_end']),
                    forecast_interval='30min',
                    forecasted_mw={
                        'ghi': forecast['ghi'],
                        'dni': forecast['dni'],
                        'dhi': forecast['dhi']
                    }
                )
                db.session.add(new_forecast)
        
        else:
            print(f"Error fetching data for location {location.id}: {response.status_code}")
    
    db.session.commit()

if __name__ == "__main__":
    fetch_solcast_data()