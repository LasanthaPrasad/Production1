from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from app.models import ForecastLocation, GridSubstation, Feeder, SolarPlant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://') or 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def init_db():
    # Clear existing data
    #db.reflect()
    #db.drop_all()

    # Create tables in the correct order
    db.create_all()

    # Create sample data for Sri Lanka
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
    db.session.commit()

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
    db.session.commit()

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
    db.session.commit()

with app.app_context():
    init_db()
