from app import create_app, db
from app.models import (
    PowerPlant, ForecastLocation, ForecastingProvider, GridSubstation,
    Feeder, FeederOutage, SolarForecastData, HydroForecastData, WindForecastData, HydroPlant
)
from datetime import datetime, timedelta
import random
from sqlalchemy.exc import ProgrammingError, OperationalError

app = create_app()

def init_db():
    with app.app_context():
        # Try to create tables
        try:
            db.drop_all()
            db.create_all()
            db.session.commit()
            print("Database tables created successfully.")
        except (ProgrammingError, OperationalError) as e:
            print(f"Error creating tables: {e}")
            db.session.rollback()
            return

        # Verify tables exist before inserting data
        try:
            # Check if GridSubstation table exists
            GridSubstation.query.first()
        except ProgrammingError as e:
            print(f"Error: Tables not created properly. {e}")
            return

        try:
            # Add Grid Substations
            substations = [
                GridSubstation(substation_name="Anuradhapura", latitude=8.3114, longitude=80.4037),
                GridSubstation(substation_name="Biyagama", latitude=6.9428, longitude=80.0139),
                GridSubstation(substation_name="Colombo", latitude=6.9271, longitude=79.8612),
                GridSubstation(substation_name="Hambantota", latitude=6.1240, longitude=81.1185),
                GridSubstation(substation_name="Vavuniya", latitude=8.7514, longitude=80.4970),
                GridSubstation(substation_name="Kilinochchi", latitude=9.3803, longitude=80.4036)
            ]
            db.session.add_all(substations)
            db.session.commit()

            # Add Feeders
            feeders = [
                Feeder(feeder_number="ANU-F1", feeder_status="Active", grid_substation_id=1),
                Feeder(feeder_number="BIY-F1", feeder_status="Active", grid_substation_id=2),
                Feeder(feeder_number="COL-F1", feeder_status="Active", grid_substation_id=3),
                Feeder(feeder_number="HAM-F1", feeder_status="Active", grid_substation_id=4),
                Feeder(feeder_number="VAV-F1", feeder_status="Active", grid_substation_id=5),
                Feeder(feeder_number="KIL-F1", feeder_status="Active", grid_substation_id=6)
            ]
            db.session.add_all(feeders)
            db.session.commit()

            # Add Power Plants
            plants = [
                PowerPlant(plant_name="Hambantota Solar Park", plant_type="Solar", latitude=6.1240, longitude=81.1185,
                           installed_capacity_mw=100, connected_grid_substation_id=4, connected_feeder_id=4),
                PowerPlant(plant_name="Mannar Wind Power Project", plant_type="Wind", latitude=8.9880, longitude=79.9080,
                           installed_capacity_mw=100, connected_grid_substation_id=1, connected_feeder_id=1),
                PowerPlant(plant_name="Mahaweli Complex", plant_type="Hydro", latitude=7.1480, longitude=80.5640,
                           installed_capacity_mw=660, connected_grid_substation_id=2, connected_feeder_id=2),
                PowerPlant(plant_name="Samanalawewa", plant_type="Hydro", latitude=6.5667, longitude=80.7333,
                           installed_capacity_mw=120, connected_grid_substation_id=3, connected_feeder_id=3),
                PowerPlant(plant_name="Puttalam Wind Farm", plant_type="Wind", latitude=8.0388, longitude=79.8417,
                           installed_capacity_mw=100, connected_grid_substation_id=5, connected_feeder_id=5),
                PowerPlant(plant_name="Soorya Bala Sangramaya", plant_type="Solar", latitude=6.9271, longitude=79.8612,
                           installed_capacity_mw=50, connected_grid_substation_id=6, connected_feeder_id=6)
            ]
            db.session.add_all(plants)
            db.session.commit()

            # Add Hydro Plant details
            hydro_plants = [
                HydroPlant(plant_id=3, catchment_area=3100, plant_efficiency=0.9, mw_per_m3=0.00323),
                HydroPlant(plant_id=4, catchment_area=1400, plant_efficiency=0.85, mw_per_m3=0.00310)
            ]
            db.session.add_all(hydro_plants)
            db.session.commit()

            # Add Forecast Locations
            locations = [
                ForecastLocation(location_name="Colombo", latitude=6.9271, longitude=79.8612, area_name="Western Province"),
                ForecastLocation(location_name="Kandy", latitude=7.2906, longitude=80.6337, area_name="Central Province"),
                ForecastLocation(location_name="Galle", latitude=6.0535, longitude=80.2210, area_name="Southern Province"),
                ForecastLocation(location_name="Jaffna", latitude=9.6615, longitude=80.0255, area_name="Northern Province"),
                ForecastLocation(location_name="Trincomalee", latitude=8.5874, longitude=81.2152, area_name="Eastern Province"),
                ForecastLocation(location_name="Anuradhapura", latitude=8.3114, longitude=80.4037, area_name="North Central Province")
            ]
            db.session.add_all(locations)
            db.session.commit()

            # Add Forecasting Providers
            providers = [
                ForecastingProvider(provider_name="Solcast", api_key="solcast_api_key_here", api_endpoint="https://api.solcast.com.au", service_type="Solar"),
                ForecastingProvider(provider_name="OpenWeatherMap", api_key="openweathermap_api_key_here", api_endpoint="https://api.openweathermap.org/data/2.5/forecast", service_type="Wind"),
                ForecastingProvider(provider_name="Weatherbit", api_key="weatherbit_api_key_here", api_endpoint="https://api.weatherbit.io/v2.0/forecast/daily", service_type="Hydro")
            ]
            db.session.add_all(providers)
            db.session.commit()

            # Add sample forecast data
            now = datetime.utcnow()
            for i in range(24):  # 24 hours of forecast data
                timestamp = now + timedelta(hours=i)
                solar_forecast = SolarForecastData(
                    plant_id=1, forecast_location_id=1, provider_id=1,
                    latitude=6.1240, longitude=81.1185,
                    ghi=random.uniform(0, 1000), dni=random.uniform(0, 800), dhi=random.uniform(0, 200),
                    air_temp=random.uniform(25, 35), zenith=random.uniform(0, 90), azimuth=random.uniform(0, 360),
                    cloud_opacity=random.uniform(0, 100), forecast_timestamp=timestamp
                )
                wind_forecast = WindForecastData(
                    plant_id=2, forecast_location_id=2, provider_id=2,
                    latitude=8.9880, longitude=79.9080,
                    wind_speed=random.uniform(0, 20), wind_direction=random.uniform(0, 360),
                    forecast_timestamp=timestamp
                )
                hydro_forecast = HydroForecastData(
                    plant_id=3, forecast_location_id=3, provider_id=3,
                    latitude=7.1480, longitude=80.5640,
                    precipitation=random.uniform(0, 50),
                    forecast_timestamp=timestamp
                )
                db.session.add_all([solar_forecast, wind_forecast, hydro_forecast])

            # Add a sample feeder outage
            outage = FeederOutage(
                feeder_id=1,
                outage_start_time=now + timedelta(days=1),
                outage_end_time=now + timedelta(days=1, hours=4),
                reason="Scheduled maintenance"
            )
            db.session.add(outage)

            db.session.commit()
            print("Database initialized with sample data for Sri Lanka.")
        except Exception as e:
            print(f"Error inserting data: {e}")
            db.session.rollback()

if __name__ == '__main__':
    init_db()