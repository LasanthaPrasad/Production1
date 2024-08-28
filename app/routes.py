from flask import Blueprint, render_template, jsonify
from app import Session
from app.models import PowerPlant, GridSubstation, ForecastLocation, SolarForecastData, WindForecastData, HydroForecastData

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/plants')
def get_plants():
    session = Session()
    plants = session.query(PowerPlant).all()
    plant_list = [{
        'id': plant.plant_id,
        'name': plant.plant_name,
        'type': plant.plant_type,
        'lat': plant.latitude,
        'lng': plant.longitude,
        'capacity': plant.installed_capacity_mw
    } for plant in plants]
    session.close()
    return jsonify(plant_list)

@main.route('/api/substations')
def get_substations():
    session = Session()
    substations = session.query(GridSubstation).all()
    substation_list = [{
        'id': sub.grid_substation_id,
        'name': sub.substation_name,
        'lat': sub.latitude,
        'lng': sub.longitude
    } for sub in substations]
    session.close()
    return jsonify(substation_list)

@main.route('/api/forecast_locations')
def get_forecast_locations():
    session = Session()
    locations = session.query(ForecastLocation).all()
    location_list = [{
        'id': loc.forecast_location_id,
        'name': loc.location_name,
        'lat': loc.latitude,
        'lng': loc.longitude
    } for loc in locations]
    session.close()
    return jsonify(location_list)

@main.route('/api/forecast/<int:plant_id>')
def get_plant_forecast(plant_id):
    session = Session()
    plant = session.query(PowerPlant).get_or_404(plant_id)
    if plant.plant_type == 'Solar':
        forecast_data = session.query(SolarForecastData).filter_by(plant_id=plant_id).order_by(SolarForecastData.forecast_timestamp.desc()).limit(24).all()
    elif plant.plant_type == 'Wind':
        forecast_data = session.query(WindForecastData).filter_by(plant_id=plant_id).order_by(WindForecastData.forecast_timestamp.desc()).limit(24).all()
    elif plant.plant_type == 'Hydro':
        forecast_data = session.query(HydroForecastData).filter_by(plant_id=plant_id).order_by(HydroForecastData.forecast_timestamp.desc()).limit(24).all()
    else:
        session.close()
        return jsonify({"error": "Invalid plant type"}), 400

    forecast_list = [data.to_dict() for data in forecast_data]
    session.close()
    return jsonify(forecast_list)