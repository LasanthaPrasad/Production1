import requests
from datetime import datetime, timedelta
import math
from app import Session
from app.models import PowerPlant, ForecastingProvider, SolarForecastData, WindForecastData, HydroForecastData, HydroPlant, GridSubstation


def fetch_solar_forecast(app):
    with app.app_context():
        session = Session()
        try:
            solcast_provider = session.query(ForecastingProvider).filter_by(provider_name="Solcast", service_type="Solar").first()
            if not solcast_provider:
                print("Solcast provider not found")
                return

            solar_plants = session.query(PowerPlant).filter_by(plant_type='Solar').all()
            for plant in solar_plants:
                response = requests.get(
                    solcast_provider.api_endpoint,
                    params={
                        'latitude': plant.latitude,
                        'longitude': plant.longitude,
                        'api_key': solcast_provider.api_key,
                        'format': 'json'
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    for forecast in data.get('forecasts', []):
                        solar_forecast = SolarForecastData(
                            plant_id=plant.plant_id,
                            provider_id=solcast_provider.provider_id,
                            latitude=plant.latitude,
                            longitude=plant.longitude,
                            ghi=forecast.get('ghi', 0),
                            dni=forecast.get('dni', 0),
                            dhi=forecast.get('dhi', 0),
                            air_temp=forecast.get('air_temp', 0),
                            cloud_opacity=forecast.get('cloud_opacity', 0),
                            forecast_timestamp=datetime.fromisoformat(forecast['period_end'])
                        )
                        session.add(solar_forecast)
                    
                    session.commit()
                    update_plant_forecast(session, plant, data['forecasts'])
                else:
                    print(f"Error fetching Solcast data for plant {plant.plant_name}: {response.status_code}")
        finally:
            session.close()

def fetch_wind_forecast(app):
    with app.app_context():
        session = Session()
        try:
            wind_provider = session.query(ForecastingProvider).filter_by(service_type="Wind").first()
            if not wind_provider:
                print("Wind forecast provider not found")
                return

            wind_plants = session.query(PowerPlant).filter_by(plant_type='Wind').all()
            for plant in wind_plants:
                response = requests.get(
                    wind_provider.api_endpoint,
                    params={
                        'lat': plant.latitude,
                        'lon': plant.longitude,
                        'key': wind_provider.api_key,
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    for i, forecast in enumerate(data.get('hourly', {}).get('windspeed_10m', [])):
                        timestamp = datetime.utcnow() + timedelta(hours=i)
                        wind_forecast = WindForecastData(
                            plant_id=plant.plant_id,
                            provider_id=wind_provider.provider_id,
                            latitude=plant.latitude,
                            longitude=plant.longitude,
                            wind_speed=forecast,
                            wind_direction=data['hourly']['winddirection_10m'][i],
                            forecast_timestamp=timestamp
                        )
                        session.add(wind_forecast)
                    
                    session.commit()
                    update_plant_forecast(session, plant, data['hourly']['windspeed_10m'])
                else:
                    print(f"Error fetching wind data for plant {plant.plant_name}: {response.status_code}")
        finally:
            session.close()

def fetch_hydro_forecast(app):
    with app.app_context():
        session = Session()
        try:
            hydro_provider = session.query(ForecastingProvider).filter_by(service_type="Hydro").first()
            if not hydro_provider:
                print("Hydro forecast provider not found")
                return

            hydro_plants = session.query(PowerPlant).filter_by(plant_type='Hydro').all()
            for plant in hydro_plants:
                response = requests.get(
                    hydro_provider.api_endpoint,
                    params={
                        'lat': plant.latitude,
                        'lon': plant.longitude,
                        'key': hydro_provider.api_key,
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    for i, forecast in enumerate(data.get('hourly', {}).get('precipitation', [])):
                        timestamp = datetime.utcnow() + timedelta(hours=i)
                        hydro_forecast = HydroForecastData(
                            plant_id=plant.plant_id,
                            provider_id=hydro_provider.provider_id,
                            latitude=plant.latitude,
                            longitude=plant.longitude,
                            precipitation=forecast,
                            forecast_timestamp=timestamp
                        )
                        session.add(hydro_forecast)
                    
                    session.commit()
                    update_plant_forecast(session, plant, data['hourly']['precipitation'])
                else:
                    print(f"Error fetching hydro data for plant {plant.plant_name}: {response.status_code}")
        finally:
            session.close()

def update_plant_forecast(session, plant, forecast_data):
    if plant.plant_type == 'Solar':
        plant.forecast_1_hour_mw = calculate_solar_power(forecast_data[0], plant)
        plant.forecast_1_day_mw = sum(calculate_solar_power(f, plant) for f in forecast_data[:24]) / 24
    elif plant.plant_type == 'Wind':
        plant.forecast_1_hour_mw = calculate_wind_power(forecast_data[0], plant)
        plant.forecast_1_day_mw = sum(calculate_wind_power(f, plant) for f in forecast_data[:24]) / 24
    elif plant.plant_type == 'Hydro':
        hydro_plant = session.query(HydroPlant).get(plant.plant_id)
        plant.forecast_1_hour_mw = calculate_hydro_power(forecast_data[0], hydro_plant)
        plant.forecast_1_day_mw = sum(calculate_hydro_power(f, hydro_plant) for f in forecast_data[:24]) / 24
    
    session.commit()

def calculate_solar_power(forecast, plant):
    ghi = forecast.get('ghi', 0)
    dni = forecast.get('dni', 0)
    dhi = forecast.get('dhi', 0)
    cloud_opacity = forecast.get('cloud_opacity', 0)
    
    effective_irradiance = ghi + dni * 0.3 + dhi * 0.5  # Simplified formula
    cloud_factor = 1 - (cloud_opacity / 100)
    raw_output = (effective_irradiance / 1000) * plant.installed_capacity_mw * cloud_factor
    return min(raw_output, plant.installed_capacity_mw)

def calculate_wind_power(wind_speed, plant):
    if wind_speed < 3 or wind_speed > 25:
        return 0
    elif wind_speed < 13:
        return plant.installed_capacity_mw * (wind_speed - 3) / 10
    else:
        return plant.installed_capacity_mw

def calculate_hydro_power(precipitation, hydro_plant):
    water_flow = hydro_plant.catchment_area * precipitation
    power_output = water_flow * hydro_plant.mw_per_m3 * hydro_plant.plant_efficiency
    return min(power_output, hydro_plant.plant.installed_capacity_mw)

def aggregate_substation_forecast(session, substation):
    plants = session.query(PowerPlant).filter_by(connected_grid_substation_id=substation.grid_substation_id).all()
    
    total_solar = sum(p.forecast_1_hour_mw for p in plants if p.plant_type == 'Solar')
    total_wind = sum(p.forecast_1_hour_mw for p in plants if p.plant_type == 'Wind')
    total_hydro = sum(p.forecast_1_hour_mw for p in plants if p.plant_type == 'Hydro')
    
    substation.total_connected_mw_solar = total_solar
    substation.total_connected_mw_wind = total_wind
    substation.total_connected_mw_hydro = total_hydro
    
    session.commit()

def update_all_forecasts(app):
    fetch_solar_forecast(app)
    fetch_wind_forecast(app)
    fetch_hydro_forecast(app)
    
    with app.app_context():
        session = Session()
        try:
            substations = session.query(GridSubstation).all()
            for substation in substations:
                aggregate_substation_forecast(session, substation)
        finally:
            session.close()