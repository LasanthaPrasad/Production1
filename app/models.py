from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class PowerPlant(db.Model):
    __tablename__ = 'power_plants'
    plant_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plant_name = db.Column(db.String(255), nullable=False)
    plant_type = db.Column(db.Enum('Solar', 'Wind', 'Hydro', 'Bio-mass', 'Thermal', name='plant_type_enum'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    installed_capacity_mw = db.Column(db.Float, nullable=False)
    real_time_mw = db.Column(db.Float)
    real_time_mvar = db.Column(db.Float)
    forecast_1_hour_mw = db.Column(db.Float)
    forecast_1_day_mw = db.Column(db.Float)
    forecast_7_day_energy = db.Column(db.Float)
    connected_grid_substation_id = db.Column(db.Integer, db.ForeignKey('grid_substations.grid_substation_id'))
    connected_feeder_id = db.Column(db.Integer, db.ForeignKey('feeders.feeder_id'))
    feeder_number = db.Column(db.String(100))
    plant_contact_number = db.Column(db.String(20))
    plant_account_number = db.Column(db.String(100))
    plant_company_name = db.Column(db.String(255))
    cloud_cover = db.Column(db.Float)
    plant_area = db.Column(db.String(255))
    division = db.Column(db.String(50))
    plant_account_type = db.Column(db.Enum('Net Metering', 'Net Account', 'Net Plus Plus', name='account_type_enum'))

class ForecastLocation(db.Model):
    __tablename__ = 'forecast_locations'
    forecast_location_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    location_name = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    area_name = db.Column(db.String(255))
    division = db.Column(db.String(50))

class ForecastingProvider(db.Model):
    __tablename__ = 'forecasting_providers'
    provider_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    provider_name = db.Column(db.String(255), nullable=False)
    api_key = db.Column(db.Text)
    api_endpoint = db.Column(db.String(255))
    service_type = db.Column(db.Enum('Solar', 'Wind', 'Hydro', name='service_type_enum'), nullable=False)

class GridSubstation(db.Model):
    __tablename__ = 'grid_substations'
    grid_substation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    substation_name = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    total_connected_mw_solar = db.Column(db.Float)
    total_connected_mw_wind = db.Column(db.Float)
    total_connected_mw_hydro = db.Column(db.Float)
    total_connected_mw_biomass = db.Column(db.Float)
    total_connected_mw_thermal = db.Column(db.Float)

class Feeder(db.Model):
    __tablename__ = 'feeders'
    feeder_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    feeder_number = db.Column(db.String(100), nullable=False)
    feeder_status = db.Column(db.Enum('Active', 'Outage', name='feeder_status_enum'), nullable=False)
    grid_substation_id = db.Column(db.Integer, db.ForeignKey('grid_substations.grid_substation_id'), nullable=False)

class FeederOutage(db.Model):
    __tablename__ = 'feeder_outages'
    outage_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    feeder_id = db.Column(db.Integer, db.ForeignKey('feeders.feeder_id'), nullable=False)
    outage_start_time = db.Column(db.DateTime, nullable=False)
    outage_end_time = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.Text)

class SolarForecastData(db.Model):
    __tablename__ = 'solar_forecast_data'
    forecast_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('power_plants.plant_id'))
    forecast_location_id = db.Column(db.Integer, db.ForeignKey('forecast_locations.forecast_location_id'))
    provider_id = db.Column(db.Integer, db.ForeignKey('forecasting_providers.provider_id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    ghi = db.Column(db.Float)
    dni = db.Column(db.Float)
    dhi = db.Column(db.Float)
    air_temp = db.Column(db.Float)
    zenith = db.Column(db.Float)
    azimuth = db.Column(db.Float)
    cloud_opacity = db.Column(db.Float)
    forecast_timestamp = db.Column(db.DateTime, nullable=False)
    forecast_created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HydroForecastData(db.Model):
    __tablename__ = 'hydro_forecast_data'
    forecast_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('power_plants.plant_id'))
    forecast_location_id = db.Column(db.Integer, db.ForeignKey('forecast_locations.forecast_location_id'))
    provider_id = db.Column(db.Integer, db.ForeignKey('forecasting_providers.provider_id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    precipitation = db.Column(db.Float)
    forecast_timestamp = db.Column(db.DateTime, nullable=False)
    forecast_created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WindForecastData(db.Model):
    __tablename__ = 'wind_forecast_data'
    forecast_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('power_plants.plant_id'))
    forecast_location_id = db.Column(db.Integer, db.ForeignKey('forecast_locations.forecast_location_id'))
    provider_id = db.Column(db.Integer, db.ForeignKey('forecasting_providers.provider_id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    wind_speed = db.Column(db.Float)
    wind_direction = db.Column(db.Float)
    forecast_timestamp = db.Column(db.DateTime, nullable=False)
    forecast_created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HydroPlant(db.Model):
    __tablename__ = 'hydro_plants'
    plant_id = db.Column(db.Integer, db.ForeignKey('power_plants.plant_id'), primary_key=True)
    catchment_area = db.Column(db.Float)
    plant_efficiency = db.Column(db.Float)
    mw_per_m3 = db.Column(db.Float)