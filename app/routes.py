from flask import Blueprint, render_template, redirect, url_for, request
from app.models import db, SolarPlant, GridSubstation, Feeder, ForecastLocation
import requests
import schedule
import time
import os

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    total_solar_capacity = sum(plant.installed_capacity for plant in SolarPlant.query.all())
    total_substation_capacity = sum(substation.installed_solar_capacity for substation in GridSubstation.query.all())
    total_plant_forecast = sum(location.next_hour_forecast['ghi'] for location in ForecastLocation.query.all())
    total_substation_forecast = sum(location.next_hour_forecast['ghi'] for location in ForecastLocation.query.all())
    forecast_locations = ForecastLocation.query.all()
    return render_template('index.html', total_solar_capacity=total_solar_capacity,
                           total_substation_capacity=total_substation_capacity,
                           total_plant_forecast=total_plant_forecast,
                           total_substation_forecast=total_substation_forecast,
                           forecast_locations=forecast_locations,
                           google_maps_api_key=os.getenv('GOOGLE_MAPS_API_KEY'))

@bp.route('/solar-plants', methods=['GET', 'POST'])
def solar_plants():
    if request.method == 'POST':
        # Handle create/update solar plant
        pass
    elif request.method == 'GET':
        solar_plants = SolarPlant.query.all()
        return render_template('solar_plants.html', solar_plants=solar_plants)

@bp.route('/solar-plants/<int:id>', methods=['GET', 'POST', 'DELETE'])
def solar_plant_detail(id):
    solar_plant = SolarPlant.query.get(id)
    if request.method == 'POST':
        # Handle update solar plant
        pass
    elif request.method == 'DELETE':
        # Handle delete solar plant
        pass
    return render_template('solar_plant_detail.html', solar_plant=solar_plant)