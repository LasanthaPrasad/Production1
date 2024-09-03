from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://') or 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class SolarPlant(db.Model):
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

class GridSubstation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    forecast_location_id = db.Column(db.Integer, db.ForeignKey('forecastlocation.id'), nullable=False)
    installed_solar_capacity = db.Column(db.Float, nullable=False)

class Feeder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    grid_substation_id = db.Column(db.Integer, db.ForeignKey('gridsubstation.id'), nullable=False)
    installed_solar_capacity = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    outage_start = db.Column(db.DateTime)
    outage_end = db.Column(db.DateTime)

class ForecastLocation(db.Model):
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

def init_db():
    # Create sample data for Sri Lanka
    solar_plant = SolarPlant(
        name='Hambantota Solar Power Plant', latitude=6.1344, longitude=81.1248,
        grid_substation_id=1, feeder_id=1, forecast_location_id=1,
        installed_capacity=50.0, panel_capacity=60.0, inverter_capacity=55.0,
        plant_angle=20.0, company='Ceylon Electricity Board'
    )
    solar_plant2 = SolarPlant(
        name='Jaffna Solar Power Plant', latitude=9.6633, longitude=80.0216,
        grid_substation_id=2, feeder_id=2, forecast_location_id=2,
        installed_capacity=40.0, panel_capacity=50.0, inverter_capacity=45.0,
        plant_angle=25.0, company='Ceylon Electricity Board'
    )
    db.session.add(solar_plant)
    db.session.add(solar_plant2)

    grid_substation1 = GridSubstation(
        name='Hambantota Grid Substation', code='GS-001',
        latitude=6.1344, longitude=81.1248, forecast_location_id=1,
        installed_solar_capacity=50.0
    )
    grid_substation2 = GridSubstation(
        name='Jaffna Grid Substation', code='GS-002',
        latitude=9.6633, longitude=80.0216, forecast_location_id=2,
        installed_solar_capacity=40.0
    )
    db.session.add(grid_substation1)
    db.session.add(grid_substation2)

    feeder1 = Feeder(
        name='Hambantota Feeder 1', code='F-001',
        grid_substation_id=1, installed_solar_capacity=25.0,
        status='active'
    )
    feeder2 = Feeder(
        name='Jaffna Feeder 1', code='F-002',
        grid_substation_id=2, installed_solar_capacity=20.0,
        status='active'
    )
    db.session.add(feeder1)
    db.session.add(feeder2)

    forecast_location1 = ForecastLocation(
        provider_name='Solcast',
        latitude=6.1344, longitude=81.1248,
        ghi=0.0, dni=0.0, dhi=0.0,
        air_temperature=30.0, zenith=45.0, azimuth=180.0,
        cloud_opacity=0.5,
        next_hour_forecast={'ghi': 0.8, 'dni': 0.6, 'dhi': 0.2},
        next_24_hours_forecast={'ghi': [0.7, 0.8, 0.9, 1.0, 0.9, 0.8], 'dni': [0.5, 0.6, 0.7, 0.8, 0.7, 0.6], 'dhi': [0.2, 0.2, 0.3, 0.3, 0.2, 0.2]}
    )
    forecast_location2 = ForecastLocation(
        provider_name='Solcast',
        latitude=9.6633, longitude=80.0216,
        ghi=0.0, dni=0.0, dhi=0.0,
        air_temperature=32.0, zenith=50.0, azimuth=190.0,
        cloud_opacity=0.6,
        next_hour_forecast={'ghi': 0.7, 'dni': 0.5, 'dhi': 0.2},
        next_24_hours_forecast={'ghi': [0.6, 0.7, 0.8, 0.9, 0.8, 0.7], 'dni': [0.4, 0.5, 0.6, 0.7, 0.6, 0.5], 'dhi': [0.2, 0.2, 0.2, 0.3, 0.2, 0.2]}
    )
    db.session.add(forecast_location1)
    db.session.add(forecast_location2)

    db.session.commit()

if __name__ == '__main__':
    db.create_all()
    init_db()