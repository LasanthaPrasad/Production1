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
        return redirect(url_for('main.solar_plants'))
    elif request.method == 'GET':
        solar_plants = SolarPlant.query.all()
        return render_template('solar_plants.html', solar_plants=solar_plants)

@bp.route('/solar-plants/<int:id>', methods=['GET', 'POST', 'DELETE'])
def solar_plant_detail(id):
    if id == 0:
        solar_plant = SolarPlant(
            name='', latitude=0.0, longitude=0.0,
            grid_substation_id=0, feeder_id=0, forecast_location_id=0,
            installed_capacity=0.0, panel_capacity=0.0, inverter_capacity=0.0,
            plant_angle=0.0, company=''
        )
    else:
        solar_plant = SolarPlant.query.get(id)



@bp.route('/solar-plants/<int:id>', methods=['GET', 'POST', 'DELETE'])
def solar_plant_detail(id):

    if id == 0:
        solar_plant = SolarPlant(
            name='', latitude=0.0, longitude=0.0,
            grid_substation_id=0, feeder_id=0, forecast_location_id=0,
            installed_capacity=0.0, panel_capacity=0.0, inverter_capacity=0.0,
            plant_angle=0.0, company=''
        )
    else:
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
        return redirect(url_for('main.solar_plants'))
    elif request.method == 'DELETE':
        # Handle delete solar plant
        db.session.delete(solar_plant)
        db.session.commit()
        return redirect(url_for('main.solar_plants'))
    return render_template('solar_plant_detail.html', solar_plant=solar_plant)

@bp.route('/grid-substations', methods=['GET', 'POST'])
def grid_substations():
    if request.method == 'POST':
        # Handle create/update grid substation
        name = request.form['name']
        code = request.form['code']
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        forecast_location_id = int(request.form['forecast_location_id'])
        installed_solar_capacity = float(request.form['installed_solar_capacity'])

        grid_substation = GridSubstation(
            name=name, code=code, latitude=latitude, longitude=longitude,
            forecast_location_id=forecast_location_id, installed_solar_capacity=installed_solar_capacity
        )
        db.session.add(grid_substation)
        db.session.commit()
        return redirect(url_for('main.grid_substations'))
    elif request.method == 'GET':
        grid_substations = GridSubstation.query.all()
        return render_template('grid_substations.html', grid_substations=grid_substations)

@bp.route('/grid-substations/<int:id>', methods=['GET', 'POST', 'DELETE'])
def grid_substation_detail(id):
    grid_substation = GridSubstation.query.get(id)
    if request.method == 'POST':
        # Handle update grid substation
        grid_substation.name = request.form['name']
        grid_substation.code = request.form['code']
        grid_substation.latitude = float(request.form['latitude'])
        grid_substation.longitude = float(request.form['longitude'])
        grid_substation.forecast_location_id = int(request.form['forecast_location_id'])
        grid_substation.installed_solar_capacity = float(request.form['installed_solar_capacity'])
        db.session.commit()
        return redirect(url_for('main.grid_substations'))
    elif request.method == 'DELETE':
        # Handle delete grid substation
        db.session.delete(grid_substation)
        db.session.commit()
        return redirect(url_for('main.grid_substations'))
    return render_template('grid_substation_detail.html', grid_substation=grid_substation)

@bp.route('/feeders', methods=['GET', 'POST'])
def feeders():
    if request.method == 'POST':
        # Handle create/update feeder
        name = request.form['name']
        code = request.form['code']
        grid_substation_id = int(request.form['grid_substation_id'])
        installed_solar_capacity = float(request.form['installed_solar_capacity'])
        status = request.form['status']
        outage_start = request.form['outage_start']
        outage_end = request.form['outage_end']

        feeder = Feeder(
            name=name, code=code, grid_substation_id=grid_substation_id,
            installed_solar_capacity=installed_solar_capacity, status=status,
            outage_start=outage_start, outage_end=outage_end
        )
        db.session.add(feeder)
        db.session.commit()
        return redirect(url_for('main.feeders'))
    elif request.method == 'GET':
        feeders = Feeder.query.all()
        return render_template('feeders.html', feeders=feeders)

@bp.route('/feeders/<int:id>', methods=['GET', 'POST', 'DELETE'])
def feeder_detail(id):
    feeder = Feeder.query.get(id)
    if request.method == 'POST':
        # Handle update feeder
        feeder.name = request.form['name']
        feeder.code = request.form['code']
        feeder.grid_substation_id = int(request.form['grid_substation_id'])
        feeder.installed_solar_capacity = float(request.form['installed_solar_capacity'])
        feeder.status = request.form['status']
        feeder.outage_start = request.form['outage_start']
        feeder.outage_end = request.form['outage_end']
        db.session.commit()
        return redirect(url_for('main.feeders'))
    elif request.method == 'DELETE':
        # Handle delete feeder
        db.session.delete(feeder)
        db.session.commit()
        return redirect(url_for('main.feeders'))
    return render_template('feeder_detail.html', feeder=feeder)


@bp.route('/forecast-locations', methods=['GET', 'POST'])
def forecast_locations():
    if request.method == 'POST':
        # Handle create/update forecast location
        provider_name = request.form['provider_name']
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        ghi = float(request.form['ghi'])
        dni = float(request.form['dni'])
        dhi = float(request.form['dhi'])
        air_temperature = float(request.form['air_temperature'])
        zenith = float(request.form['zenith'])
        azimuth = float(request.form['azimuth'])
        cloud_opacity = float(request.form['cloud_opacity'])
        next_hour_forecast = request.form['next_hour_forecast']
        next_24_hours_forecast = request.form['next_24_hours_forecast']

        forecast_location = ForecastLocation(
            provider_name=provider_name, latitude=latitude, longitude=longitude,
            ghi=ghi, dni=dni, dhi=dhi, air_temperature=air_temperature,
            zenith=zenith, azimuth=azimuth, cloud_opacity=cloud_opacity,
            next_hour_forecast=next_hour_forecast, next_24_hours_forecast=next_24_hours_forecast
        )
        db.session.add(forecast_location)
        db.session.commit()
        return redirect(url_for('main.forecast_locations'))
    elif request.method == 'GET':
        forecast_locations = ForecastLocation.query.all()
        return render_template('forecast_locations.html', forecast_locations=forecast_locations)

@bp.route('/forecast-locations/<int:id>', methods=['GET', 'POST', 'DELETE'])
def forecast_location_detail(id):
    forecast_location = ForecastLocation.query.get(id)
    if request.method == 'POST':
        # Handle update forecast location
        forecast_location.provider_name = request.form['provider_name']
        forecast_location.latitude = float(request.form['latitude'])
        forecast_location.longitude = float(request.form['longitude'])
        forecast_location.ghi = float(request.form['ghi'])
        forecast_location.dni = float(request.form['dni'])
        forecast_location.dhi = float(request.form['dhi'])
        forecast_location.air_temperature = float(request.form['air_temperature'])
        forecast_location.zenith = float(request.form['zenith'])
        forecast_location.azimuth = float(request.form['azimuth'])
        forecast_location.cloud_opacity = float(request.form['cloud_opacity'])
        forecast_location.next_hour_forecast = request.form['next_hour_forecast']
        forecast_location.next_24_hours_forecast = request.form['next_24_hours_forecast']
        db.session.commit()
        return redirect(url_for('main.forecast_locations'))
    elif request.method == 'DELETE':
        # Handle delete forecast location
        db.session.delete(forecast_location)
        db.session.commit()
        return redirect(url_for('main.forecast_locations'))
    return render_template('forecast_location_detail.html', forecast_location=forecast_location)