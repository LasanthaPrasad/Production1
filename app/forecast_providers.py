import requests
from abc import ABC, abstractmethod
from datetime import datetime
from .models import IrradiationForecast

class BaseForecastProvider(ABC):
    @abstractmethod
    def fetch_forecast(self, location):
        pass

    @abstractmethod
    def parse_forecast(self, data):
        pass

class SolcastProvider(BaseForecastProvider):
    def fetch_forecast(self, location):
        url = "https://api.solcast.com.au/world_radiation/forecasts"
        params = {
            'latitude': location.latitude,
            'longitude': location.longitude,
            'api_key': location.api_key,
            'format': 'json',
            'hours': 168  # 7 days
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def parse_forecast(self, data):
        forecasts = []
        for forecast in data['forecasts']:
            forecasts.append(IrradiationForecast(
                timestamp=datetime.fromisoformat(forecast['period_end'].replace('Z', '+00:00')),
                ghi=forecast['ghi'],
                dni=forecast['dni'],
                dhi=forecast['dhi'],
                air_temp=forecast.get('air_temp'),
                cloud_opacity=forecast.get('cloud_opacity')
            ))
        return forecasts

class VisualCrossingProvider(BaseForecastProvider):
    def fetch_forecast(self, location):
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location.latitude},{location.longitude}"
        params = {
            'key': location.api_key,
            'include': 'hours',
            'elements': 'datetime,solarradiation,temp,cloudcover',
            'unitGroup': 'metric',
            'contentType': 'json'
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def parse_forecast(self, data):
        forecasts = []
        for day in data['days']:
            for hour in day['hours']:
                forecasts.append(IrradiationForecast(
                    timestamp=datetime.fromisoformat(hour['datetime'].replace('Z', '+00:00')),
                    ghi=hour['solarradiation'],
                    air_temp=hour['temp'],
                    cloud_opacity=hour['cloudcover'] / 100  # Convert to 0-1 scale
                ))
        return forecasts