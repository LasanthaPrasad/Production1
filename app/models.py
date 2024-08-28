from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class PowerPlant(Base):
    __tablename__ = 'power_plants'
    plant_id = Column(Integer, primary_key=True, autoincrement=True)
    plant_name = Column(String(255), nullable=False)
    plant_type = Column(Enum('Solar', 'Wind', 'Hydro', 'Bio-mass', 'Thermal', name='plant_type_enum'), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    installed_capacity_mw = Column(Float, nullable=False)
    real_time_mw = Column(Float)
    real_time_mvar = Column(Float)
    forecast_1_hour_mw = Column(Float)
    forecast_1_day_mw = Column(Float)
    forecast_7_day_energy = Column(Float)
    connected_grid_substation_id = Column(Integer, ForeignKey('grid_substations.grid_substation_id'))
    connected_feeder_id = Column(Integer, ForeignKey('feeders.feeder_id'))
    feeder_number = Column(String(100))
    plant_contact_number = Column(String(20))
    plant_account_number = Column(String(100))
    plant_company_name = Column(String(255))
    cloud_cover = Column(Float)
    plant_area = Column(String(255))
    division = Column(String(50))
    plant_account_type = Column(Enum('Net Metering', 'Net Account', 'Net Plus Plus', name='account_type_enum'))

class ForecastLocation(Base):
    __tablename__ = 'forecast_locations'
    forecast_location_id = Column(Integer, primary_key=True, autoincrement=True)
    location_name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    area_name = Column(String(255))
    division = Column(String(50))

class ForecastingProvider(Base):
    __tablename__ = 'forecasting_providers'
    provider_id = Column(Integer, primary_key=True, autoincrement=True)
    provider_name = Column(String(255), nullable=False)
    api_key = Column(String(255))
    api_endpoint = Column(String(255))
    service_type = Column(Enum('Solar', 'Wind', 'Hydro', name='service_type_enum'), nullable=False)

class GridSubstation(Base):
    __tablename__ = 'grid_substations'
    grid_substation_id = Column(Integer, primary_key=True, autoincrement=True)
    substation_name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    total_connected_mw_solar = Column(Float)
    total_connected_mw_wind = Column(Float)
    total_connected_mw_hydro = Column(Float)
    total_connected_mw_biomass = Column(Float)
    total_connected_mw_thermal = Column(Float)

class Feeder(Base):
    __tablename__ = 'feeders'
    feeder_id = Column(Integer, primary_key=True, autoincrement=True)
    feeder_number = Column(String(100), nullable=False)
    feeder_status = Column(Enum('Active', 'Outage', name='feeder_status_enum'), nullable=False)
    grid_substation_id = Column(Integer, ForeignKey('grid_substations.grid_substation_id'), nullable=False)

class FeederOutage(Base):
    __tablename__ = 'feeder_outages'
    outage_id = Column(Integer, primary_key=True, autoincrement=True)
    feeder_id = Column(Integer, ForeignKey('feeders.feeder_id'), nullable=False)
    outage_start_time = Column(DateTime, nullable=False)
    outage_end_time = Column(DateTime, nullable=False)
    reason = Column(String(255))

class SolarForecastData(Base):
    __tablename__ = 'solar_forecast_data'
    forecast_id = Column(Integer, primary_key=True, autoincrement=True)
    plant_id = Column(Integer, ForeignKey('power_plants.plant_id'))
    forecast_location_id = Column(Integer, ForeignKey('forecast_locations.forecast_location_id'))
    provider_id = Column(Integer, ForeignKey('forecasting_providers.provider_id'), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    ghi = Column(Float)
    dni = Column(Float)
    dhi = Column(Float)
    air_temp = Column(Float)
    zenith = Column(Float)
    azimuth = Column(Float)
    cloud_opacity = Column(Float)
    forecast_timestamp = Column(DateTime, nullable=False)
    forecast_created_at = Column(DateTime, default=datetime.utcnow)

class HydroForecastData(Base):
    __tablename__ = 'hydro_forecast_data'
    forecast_id = Column(Integer, primary_key=True, autoincrement=True)
    plant_id = Column(Integer, ForeignKey('power_plants.plant_id'))
    forecast_location_id = Column(Integer, ForeignKey('forecast_locations.forecast_location_id'))
    provider_id = Column(Integer, ForeignKey('forecasting_providers.provider_id'), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    precipitation = Column(Float)
    forecast_timestamp = Column(DateTime, nullable=False)
    forecast_created_at = Column(DateTime, default=datetime.utcnow)

class WindForecastData(Base):
    __tablename__ = 'wind_forecast_data'
    forecast_id = Column(Integer, primary_key=True, autoincrement=True)
    plant_id = Column(Integer, ForeignKey('power_plants.plant_id'))
    forecast_location_id = Column(Integer, ForeignKey('forecast_locations.forecast_location_id'))
    provider_id = Column(Integer, ForeignKey('forecasting_providers.provider_id'), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    wind_speed = Column(Float)
    wind_direction = Column(Float)
    forecast_timestamp = Column(DateTime, nullable=False)
    forecast_created_at = Column(DateTime, default=datetime.utcnow)

class HydroPlant(Base):
    __tablename__ = 'hydro_plants'
    plant_id = Column(Integer, ForeignKey('power_plants.plant_id'), primary_key=True)
    catchment_area = Column(Float)
    plant_efficiency = Column(Float)
    mw_per_m3 = Column(Float)