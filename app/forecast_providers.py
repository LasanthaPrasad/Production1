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
        print(f"SolcastProvider: Fetching forecast for location {location.id}")
        url = "https://api.solcast.com.au/world_radiation/forecasts"
        params = {
            'latitude': location.latitude,
            'longitude': location.longitude,
            'api_key': location.api_key,
            'format': 'json',
            'hours': 168  # 7 days
        }
        response = requests.get(url, params=params)
        print(f"SolcastProvider: API response status code: {response.status_code}")
        response.raise_for_status()
        return response.json()

    def parse_forecast(self, data):
        print("SolcastProvider: Parsing forecast data")
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
        print(f"SolcastProvider: Parsed {len(forecasts)} forecast entries")
        return forecasts



class VisualCrossingProvider(BaseForecastProvider):
    def fetch_forecast(self, location):
        print(f"VisualCrossingProvider: Fetching forecast for location {location.id}")
        coordinates = f"{location.latitude}%2C%20{location.longitude}"
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{coordinates}"
        params = {
            'key': location.api_key,
            'include': 'hours',
            'elements': 'datetime,solarradiation,temp,cloudcover',
            'unitGroup': 'us',
            'contentType': 'json'
        }
        response = requests.get(url, params=params)
        print(f"VisualCrossingProvider: API response status code: {response.status_code}")
        response.raise_for_status()
        return response.json()

    def parse_forecast(self, data):
        print("VisualCrossingProvider: Parsing forecast data")
        forecasts = []
        for day in data['days']:
            date = datetime.strptime(day['datetime'], '%Y-%m-%d')
            for hour in day['hours']:
                time = datetime.strptime(hour['datetime'], '%H:%M:%S').time()
                timestamp = datetime.combine(date, time)
                forecasts.append(IrradiationForecast(
                    timestamp=timestamp,
                    ghi=hour['solarradiation'],
                    air_temp=hour['temp'],
                    cloud_opacity=hour['cloudcover'] / 100  # Convert to 0-1 scale
                ))
        print(f"VisualCrossingProvider: Parsed {len(forecasts)} forecast entries")
        return forecasts





