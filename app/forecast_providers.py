import os
from abc import ABC, abstractmethod
import requests
from datetime import datetime
from .models import ForecastLocation, IrradiationForecast
from .extensions import db  # Import db if you're using it in this file
SOLCAST_API_KEY = os.environ.get('SOLCAST_API_KEY')
SOLCAST_BASE_URL = 'https://api.solcast.com.au/world_radiation/forecasts'



class BaseForecastProvider(ABC):
    @abstractmethod
    def fetch_forecast(self, location):
        pass

    @abstractmethod
    def parse_forecast(self, data):
        pass


class SolcastProvider(BaseForecastProvider):
    def fetch_forecast(self, location):
        # Implement Solcast API call logic here
        # This is just a placeholder, replace with actual Solcast API call
        url = f"https://api.solcast.com.au/world_radiation/forecasts?latitude={location.latitude}&longitude={location.longitude}"
        headers = {"Authorization": f"Bearer {location.api_key}"}
        response = requests.get(url, headers=headers)
        return response.json()

    def parse_forecast(self, data):
        forecasts = []
        for forecast in data['forecasts']:
            forecast = IrradiationForecast(
                timestamp=datetime.fromisoformat(forecast['period_end'].replace('Z', '+00:00')),
                ghi=forecast['ghi'],
                dni=forecast['dni'],
                dhi=forecast['dhi'],
                air_temp=forecast.get('air_temp'),
                cloud_opacity=forecast.get('cloud_opacity')
            )
            forecasts.append(forecast)
        return forecasts

class VisualCrossingProvider(BaseForecastProvider):
    def fetch_forecast(self, location):
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location.latitude},{location.longitude}"
        params = {
            'key': location.api_key,
            'include': 'hours',
            'elements': 'datetime,solarradiation,temp,cloudcover'
        }
        response = requests.get(url, params=params)
        return response.json()

    def parse_forecast(self, data):
        forecasts = []
        for day in data['days']:
            for hour in day['hours']:
                forecast = IrradiationForecast(
                    timestamp=datetime.fromisoformat(hour['datetime'].replace('Z', '+00:00')),
                    ghi=hour['solarradiation'],
                    air_temp=hour['temp'],
                    cloud_opacity=hour['cloudcover'] / 100  # Convert to 0-1 scale
                )
                forecasts.append(forecast)
        return forecasts

# OpenWeatherProvider will be added here later



