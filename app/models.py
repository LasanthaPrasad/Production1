from app import db
from datetime import datetime

class ForecastLocation(db.Model):
    __tablename__ = 'forecast_locations'
    id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)
    ghi = db.Column(db.Numeric(10, 2))
    dni = db.Column(db.Numeric(10, 2))
    dhi = db.Column(db.Numeric(10, 2))
    air_temperature = db.Column(db.Numeric(5, 2))
    zenith = db.Column(db.Numeric(5, 2))
    azimuth = db.Column(db.Numeric(5, 2))
    cloud_opacity = db.Column(db.Numeric(5, 2))
    next_hour_forecast = db.Column(db.JSON)
    next_24_hours_forecast = db.Column(db.JSON)

class GridSubstation(db.Model):
    __tablename__ = 'grid_substations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)
    forecast_location = db.Column(db.Integer, db.ForeignKey('forecast_locations.id'))
    installed_solar_capacity = db.Column(db.Numeric(10, 2))

class Feeder(db.Model):
    __tablename__ = 'feeders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    grid_substation = db.Column(db.Integer, db.ForeignKey('grid_substations.id'))
    installed_solar_capacity = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(50))
    outage_start = db.Column(db.DateTime)
    outage_end = db.Column(db.DateTime)

class SolarPlant(db.Model):
    __tablename__ = 'solar_plants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)
    grid_substation = db.Column(db.Integer, db.ForeignKey('grid_substations.id'))
    feeder = db.Column(db.Integer, db.ForeignKey('feeders.id'))
    forecast_location = db.Column(db.Integer, db.ForeignKey('forecast_locations.id'))
    installed_capacity = db.Column(db.Numeric(10, 2))
    panel_capacity = db.Column(db.Numeric(10, 2))
    inverter_capacity = db.Column(db.Numeric(10, 2))
    plant_angle = db.Column(db.Numeric(5, 2))
    company = db.Column(db.String(255))

class Forecast(db.Model):
    __tablename__ = 'forecasts'
    id = db.Column(db.Integer, primary_key=True)
    solar_plant = db.Column(db.Integer, db.ForeignKey('solar_plants.id'))
    grid_substation = db.Column(db.Integer, db.ForeignKey('grid_substations.id'))
    forecast_location = db.Column(db.Integer, db.ForeignKey('forecast_locations.id'))
    forecast_timestamp = db.Column(db.DateTime, nullable=False)
    forecast_interval = db.Column(db.String(20))
    forecasted_mw = db.Column(db.JSON)