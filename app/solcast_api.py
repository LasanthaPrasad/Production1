import requests
from datetime import datetime, timedelta
from app import db
from app.models import ForecastLocation, IrradiationForecast

SOLCAST_API_KEY = 'your_solcast_api_key_here'
SOLCAST_BASE_URL = 'https://api.solcast.com.au/world_radiation/forecasts'

def fetch_solcast_forecasts():
    locations = ForecastLocation.query.all()
    for location in locations:
        if not location.solcast_resource_id:
            continue

        params = {
            'api_key': SOLCAST_API_KEY,
            'format': 'json',
            'hours': 72  # 3 days
        }

        response = requests.get(f"{SOLCAST_BASE_URL}/{location.solcast_resource_id}", params=params)
        
        if response.status_code == 200:
            forecasts = response.json()['forecasts']
            for forecast in forecasts:
                timestamp = datetime.fromisoformat(forecast['period_end'].replace('Z', '+00:00'))
                
                existing_forecast = IrradiationForecast.query.filter_by(
                    forecast_location_id=location.id,
                    timestamp=timestamp
                ).first()

                if existing_forecast:
                    existing_forecast.ghi = forecast['ghi']
                    existing_forecast.dni = forecast['dni']
                    existing_forecast.dhi = forecast['dhi']
                    existing_forecast.air_temp = forecast['air_temp']
                    existing_forecast.cloud_opacity = forecast['cloud_opacity']
                else:
                    new_forecast = IrradiationForecast(
                        forecast_location_id=location.id,
                        timestamp=timestamp,
                        ghi=forecast['ghi'],
                        dni=forecast['dni'],
                        dhi=forecast['dhi'],
                        air_temp=forecast['air_temp'],
                        cloud_opacity=forecast['cloud_opacity']
                    )
                    db.session.add(new_forecast)

            db.session.commit()
        else:
            print(f"Error fetching forecast for location {location.id}: {response.status_code}")

    print("Forecast update completed")