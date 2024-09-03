from flask import render_template, redirect, url_for, request
from app import app, db
from app.models import SolarPlant, GridSubstation, Feeder, ForecastLocation
import requests
import schedule
import time 
import os
import json
import datetime

@app.route('/solar-plants', methods=['GET', 'POST'])
def solar_plants():
    if request.method == 'POST':
        # Handle create/update solar plant
        name = request.form['name']
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        grid_substation_id = int(request.form['grid_substation_id'])
        feeder_id = int(request.form['feeder_id'])
        forecast_location_id = int(request.form['forecast_location_id'])
        installed_capacity = float(request.form['installed_capacity'])
        panel_capacity = float(request.form['panel_capacity'])
        inverter_capacity = float(request.form['inverter_capacity'])
        plant_angle = float(request.form['plant_angle'])
        company = request.form['company']

        solar_plant = SolarPlant(
            name=name, latitude=latitude, longitude=longitude,
            grid_substation_id=grid_substation_id, feeder_id=feeder_id,
            forecast_location_id=forecast_location_id, installed_capacity=installed_capacity,
            panel_capacity=panel_capacity, inverter_capacity=inverter_capacity,
            plant_angle=plant_angle, company=company
        )
        db.session.add(solar_plant)
        db.session.commit()
        return redirect(url_for('solar_plants'))
    elif request.method == 'GET':
        solar_plants = SolarPlant.query.all()
        return render_template('solar_plants.html', solar_plants=solar_plants)

@app.route('/solar-plants/<int:id>', methods=['GET', 'POST', 'DELETE'])
def solar_plant_detail(id):
    solar_plant = SolarPlant.query.get(id)
    if request.method == 'POST':
        # Handle update solar plant
        solar_plant.name = request.form['name']
        solar_plant.latitude = float(request.form['latitude'])
        solar_plant.longitude = float(request.form['longitude'])
        solar_plant.grid_substation_id = int(request.form['grid_substation_id'])
        solar_plant.feeder_id = int(request.form['feeder_id'])
        solar_plant.forecast_location_id = int(request.form['forecast_location_id'])
        solar_plant.installed_capacity = float(request.form['installed_capacity'])
        solar_plant.panel_capacity = float(request.form['panel_capacity'])
        solar_plant.inverter_capacity = float(request.form['inverter_capacity'])
        solar_plant.plant_angle = float(request.form['plant_angle'])
        solar_plant.company = request.form['company']
        db.session.commit()
        return redirect(url_for('solar_plants'))
    elif request.method == 'DELETE':
        # Handle delete solar plant
        db.session.delete(solar_plant)
        db.session.commit()
        return redirect(url_for('solar_plants'))
    return render_template('solar_plant_detail.html', solar_plant=solar_plant)

def fetch_forecast():
 current_time = datetime.datetime.now().time()
 if current_time.hour >= 6 and current_time.hour < 18:
 
    for location in ForecastLocation.query.all():
        url = f"https://api.solcast.com.au/radiation/forecasts?latitude={location.latitude}&longitude={location.longitude}&api_key={os.getenv('SOLCAST_API_KEY')}"
        response = requests.get(url)
        forecast_data = response.json()
        location.ghi = forecast_data['ghi']
        location.dni = forecast_data['dni']
        location.dhi = forecast_data['dhi']
        location.air_temperature = forecast_data['air_temperature']
        location.zenith = forecast_data['zenith']
        location.azimuth = forecast_data['azimuth']
        location.cloud_opacity = forecast_data['cloud_opacity']
        location.next_hour_forecast = forecast_data['forecasts']['next_hour']
        location.next_24_hours_forecast = forecast_data['forecasts']['next_24_hours']
        db.session.add(location)
    db.session.commit()


schedule.every().hour.do(fetch_forecast)


#schedule.every().hour.between(6, 18).do(fetch_forecast)


@app.route('/')
def index():
    total_solar_capacity = sum(plant.installed_capacity for plant in SolarPlant.query.all())
    total_substation_capacity = sum(substation.installed_solar_capacity for substation in GridSubstation.query.all())
    total_plant_forecast = sum(location.next_hour_forecast['ghi'] for location in ForecastLocation.query.all())
    total_substation_forecast = sum(location.next_hour_forecast['ghi'] for location in ForecastLocation.query.all())
    forecast_locations = ForecastLocation.query.all()
    forecast_locations_json = json.dumps([location.to_dict() for location in forecast_locations])
    return render_template('index.html', total_solar_capacity=total_solar_capacity,
                           total_substation_capacity=total_substation_capacity,
                           total_plant_forecast=total_plant_forecast,
                           total_substation_forecast=total_substation_forecast,
                           forecast_locations_json=forecast_locations_json,
                           google_maps_api_key=os.getenv('GOOGLE_MAPS_API_KEY'))