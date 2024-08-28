from flask import Blueprint, render_template, jsonify
from app.models import PowerPlant, GridSubstation, ForecastLocation, SolarForecastData, WindForecastData, HydroForecastData
from app import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/plants')
def get_plants():
    plants = PowerPlant.query.all()
    return jsonify([{
        'id': plant.plant_id,
        'name': plant.plant_name,
        'type': plant.plant_type,
        'lat': plant.latitude,
        'lng': plant.longitude,
        'capacity': plant.installed_capacity_mw
    } for plant in plants])

@main.route('/api/substations')
def get_substations():
    substations = GridSubstation.query.all()
    return jsonify([{
        'id': sub.grid_substation_id,
        'name': sub.substation_name,
        'lat': sub.latitude,
        'lng': sub.longitude
    } for sub in substations])

@main.route('/api/forecast_locations')
def get_forecast_locations():
    locations = ForecastLocation.query.all()
    return jsonify([{
        'id': loc.forecast_location_id,
        'name': loc.location_name,
        'lat': loc.latitude,
        'lng': loc.longitude
    } for loc in locations])

@main.route('/api/forecast/<int:plant_id>')
def get_plant_forecast(plant_id):
    plant = PowerPlant.query.get_or_404(plant_id)
    if plant.plant_type == 'Solar':
        forecast_data = SolarForecastData.query.filter_by(plant_id=plant_id).order_by(SolarForecastData.forecast_timestamp.desc()).limit(24).all()
    elif plant.plant_type == 'Wind':
        forecast_data = WindForecastData.query.filter_by(plant_id=plant_id).order_by(WindForecastData.forecast_timestamp.desc()).limit(24).all()
    elif plant.plant_type == 'Hydro':
        forecast_data = HydroForecastData.query.filter_by(plant_id=plant_id).order_by(HydroForecastData.forecast_timestamp.desc()).limit(24).all()
    else:
        return jsonify({"error": "Invalid plant type"}), 400

    return jsonify([data.to_dict() for data in forecast_data])