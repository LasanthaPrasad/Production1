from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://') or 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class ForecastLocation(db.Model):
    __tablename__ = 'forecastlocation'
    id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    ghi = db.Column(db.Float, nullable=False)
    dni = db.Column(db.Float, nullable=False)
    dhi = db.Column(db.Float, nullable=False)
    air_temperature = db.Column(db.Float, nullable=False)
    zenith = db.Column(db.Float, nullable=False)
    azimuth = db.Column(db.Float, nullable=False)
    cloud_opacity = db.Column(db.Float, nullable=False)
    next_hour_forecast = db.Column(db.JSON, nullable=False)
    next_24_hours_forecast = db.Column(db.JSON, nullable=False)

class GridSubstation(db.Model):
    __tablename__ = 'gridsubstation'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    forecast_location_id = db.Column(db.Integer, db.ForeignKey('forecastlocation.id'), nullable=False)
    installed_solar_capacity = db.Column(db.Float, nullable=False)

class Feeder(db.Model):
    __tablename__ = 'feeder'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    grid_substation_id = db.Column(db.Integer, db.ForeignKey('gridsubstation.id'), nullable=False)
    installed_solar_capacity = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    outage_start = db.Column(db.DateTime)
    outage_end = db.Column(db.DateTime)

class SolarPlant(db.Model):
    __tablename__ = 'solarplant'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    grid_substation_id = db.Column(db.Integer, db.ForeignKey('gridsubstation.id'), nullable=False)
    feeder_id = db.Column(db.Integer, db.ForeignKey('feeder.id'), nullable=False)
    forecast_location_id = db.Column(db.Integer, db.ForeignKey('forecastlocation.id'), nullable=False)
    installed_capacity = db.Column(db.Float, nullable=False)
    panel_capacity = db.Column(db.Float, nullable=False)
    inverter_capacity = db.Column(db.Float, nullable=False)
    plant_angle = db.Column(db.Float, nullable=False)
    company = db.Column(db.String(100), nullable=False)