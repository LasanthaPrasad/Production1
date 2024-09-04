from app import db
from datetime import datetime

class SolarPlant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    grid_substation_id = db.Column(db.Integer, db.ForeignKey('grid_substation.id'))
    feeder_id = db.Column(db.Integer, db.ForeignKey('feeder.id'))
    forecast_location_id = db.Column(db.Integer, db.ForeignKey('forecast_location.id'))
    installed_capacity = db.Column(db.Float)
    panel_capacity = db.Column(db.Float)
    inverter_capacity = db.Column(db.Float)
    plant_angle = db.Column(db.Float)
    company = db.Column(db.String(255))

class GridSubstation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(50), unique=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    forecast_location_id = db.Column(db.Integer, db.ForeignKey('forecast_location.id'))
    installed_solar_capacity = db.Column(db.Float)

class Feeder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(50), unique=True)
    grid_substation_id = db.Column(db.Integer, db.ForeignKey('grid_substation.id'))
    installed_solar_capacity = db.Column(db.Float)
    status = db.Column(db.String(50))
    outage_start = db.Column(db.DateTime)
    outage_end = db.Column(db.DateTime)

class ForecastLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    ghi = db.Column(db.Float)
    dni = db.Column(db.Float)
    dhi = db.Column(db.Float)
    air_temperature = db.Column(db.Float)
    zenith = db.Column(db.Float)
    azimuth = db.Column(db.Float)
    cloud_opacity = db.Column(db.Float)
    next_hour_forecast = db.Column(db.JSON)
    next_24_hours_forecast = db.Column(db.JSON)

class Forecast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    solar_plant_id = db.Column(db.Integer, db.ForeignKey('solar_plant.id'))
    grid_substation_id = db.Column(db.Integer, db.ForeignKey('grid_substation.id'))
    forecast_location_id = db.Column(db.Integer, db.ForeignKey('forecast_location.id'))
    forecast_timestamp = db.Column(db.DateTime, nullable=False)
    forecast_interval = db.Column(db.String(20))
    forecasted_mw = db.Column(db.JSON)