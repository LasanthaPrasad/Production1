from flask import Blueprint, render_template, jsonify, request
from app import Session
from app.models import PowerPlant, GridSubstation, ForecastLocation, SolarForecastData, WindForecastData, HydroForecastData, Feeder, FeederOutage
from sqlalchemy import func

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/plants')
def get_plants():
    session = Session()
    try:
        plants = session.query(PowerPlant).all()
        plant_list = [{
            'id': plant.plant_id,
            'name': plant.plant_name,
            'type': plant.plant_type,
            'lat': plant.latitude,
            'lng': plant.longitude,
            'capacity': plant.installed_capacity_mw
        } for plant in plants]
        return jsonify(plant_list)
    finally:
        session.close()

@main.route('/api/substations')
def get_substations():
    session = Session()
    try:
        substations = session.query(GridSubstation).all()
        substation_list = [{
            'id': sub.grid_substation_id,
            'name': sub.substation_name,
            'lat': sub.latitude,
            'lng': sub.longitude
        } for sub in substations]
        return jsonify(substation_list)
    finally:
        session.close()

@main.route('/api/forecast_locations')
def get_forecast_locations():
    session = Session()
    try:
        locations = session.query(ForecastLocation).all()
        location_list = [{
            'id': loc.forecast_location_id,
            'name': loc.location_name,
            'lat': loc.latitude,
            'lng': loc.longitude,
            'area_name': loc.area_name
        } for loc in locations]
        return jsonify(location_list)
    finally:
        session.close()

@main.route('/api/forecast/<int:plant_id>')
def get_plant_forecast(plant_id):
    session = Session()
    try:
        plant = session.query(PowerPlant).get_or_404(plant_id)
        if plant.plant_type == 'Solar':
            forecast_data = session.query(SolarForecastData).filter_by(plant_id=plant_id).order_by(SolarForecastData.forecast_timestamp.desc()).limit(24).all()
            forecast_list = [{
                'timestamp': data.forecast_timestamp,
                'ghi': data.ghi,
                'dni': data.dni,
                'dhi': data.dhi,
                'air_temp': data.air_temp,
                'cloud_opacity': data.cloud_opacity
            } for data in forecast_data]
        elif plant.plant_type == 'Wind':
            forecast_data = session.query(WindForecastData).filter_by(plant_id=plant_id).order_by(WindForecastData.forecast_timestamp.desc()).limit(24).all()
            forecast_list = [{
                'timestamp': data.forecast_timestamp,
                'wind_speed': data.wind_speed,
                'wind_direction': data.wind_direction
            } for data in forecast_data]
        elif plant.plant_type == 'Hydro':
            forecast_data = session.query(HydroForecastData).filter_by(plant_id=plant_id).order_by(HydroForecastData.forecast_timestamp.desc()).limit(24).all()
            forecast_list = [{
                'timestamp': data.forecast_timestamp,
                'precipitation': data.precipitation
            } for data in forecast_data]
        else:
            return jsonify({"error": "Invalid plant type"}), 400
        
        return jsonify(forecast_list)
    finally:
        session.close()

@main.route('/api/substation_forecast/<int:substation_id>')
def get_substation_forecast(substation_id):
    session = Session()
    try:
        substation = session.query(GridSubstation).get_or_404(substation_id)
        plants = session.query(PowerPlant).filter_by(connected_grid_substation_id=substation_id).all()
        
        solar_forecast = session.query(
            func.avg(SolarForecastData.ghi).label('avg_ghi'),
            func.avg(SolarForecastData.dni).label('avg_dni'),
            func.avg(SolarForecastData.dhi).label('avg_dhi'),
            SolarForecastData.forecast_timestamp
        ).filter(SolarForecastData.plant_id.in_([plant.plant_id for plant in plants if plant.plant_type == 'Solar'])).group_by(SolarForecastData.forecast_timestamp).order_by(SolarForecastData.forecast_timestamp).limit(24).all()

        wind_forecast = session.query(
            func.avg(WindForecastData.wind_speed).label('avg_wind_speed'),
            func.avg(WindForecastData.wind_direction).label('avg_wind_direction'),
            WindForecastData.forecast_timestamp
        ).filter(WindForecastData.plant_id.in_([plant.plant_id for plant in plants if plant.plant_type == 'Wind'])).group_by(WindForecastData.forecast_timestamp).order_by(WindForecastData.forecast_timestamp).limit(24).all()

        hydro_forecast = session.query(
            func.avg(HydroForecastData.precipitation).label('avg_precipitation'),
            HydroForecastData.forecast_timestamp
        ).filter(HydroForecastData.plant_id.in_([plant.plant_id for plant in plants if plant.plant_type == 'Hydro'])).group_by(HydroForecastData.forecast_timestamp).order_by(HydroForecastData.forecast_timestamp).limit(24).all()

        return jsonify({
            'solar': [{
                'timestamp': data.forecast_timestamp,
                'avg_ghi': data.avg_ghi,
                'avg_dni': data.avg_dni,
                'avg_dhi': data.avg_dhi
            } for data in solar_forecast],
            'wind': [{
                'timestamp': data.forecast_timestamp,
                'avg_wind_speed': data.avg_wind_speed,
                'avg_wind_direction': data.avg_wind_direction
            } for data in wind_forecast],
            'hydro': [{
                'timestamp': data.forecast_timestamp,
                'avg_precipitation': data.avg_precipitation
            } for data in hydro_forecast]
        })
    finally:
        session.close()

@main.route('/api/feeders')
def get_feeders():
    session = Session()
    try:
        feeders = session.query(Feeder).all()
        feeder_list = [{
            'id': feeder.feeder_id,
            'number': feeder.feeder_number,
            'status': feeder.feeder_status,
            'substation_id': feeder.grid_substation_id
        } for feeder in feeders]
        return jsonify(feeder_list)
    finally:
        session.close()

@main.route('/api/feeder_outages')
def get_feeder_outages():
    session = Session()
    try:
        outages = session.query(FeederOutage).all()
        outage_list = [{
            'id': outage.outage_id,
            'feeder_id': outage.feeder_id,
            'start_time': outage.outage_start_time,
            'end_time': outage.outage_end_time,
            'reason': outage.reason
        } for outage in outages]
        return jsonify(outage_list)
    finally:
        session.close()

@main.route('/api/plant/<int:plant_id>', methods=['GET', 'PUT'])
def plant_details(plant_id):
    session = Session()
    try:
        plant = session.query(PowerPlant).get_or_404(plant_id)
        if request.method == 'GET':
            return jsonify({
                'id': plant.plant_id,
                'name': plant.plant_name,
                'type': plant.plant_type,
                'latitude': plant.latitude,
                'longitude': plant.longitude,
                'installed_capacity_mw': plant.installed_capacity_mw,
                'real_time_mw': plant.real_time_mw,
                'real_time_mvar': plant.real_time_mvar,
                'forecast_1_hour_mw': plant.forecast_1_hour_mw,
                'forecast_1_day_mw': plant.forecast_1_day_mw,
                'forecast_7_day_energy': plant.forecast_7_day_energy,
                'connected_grid_substation_id': plant.connected_grid_substation_id,
                'connected_feeder_id': plant.connected_feeder_id,
                'feeder_number': plant.feeder_number,
                'plant_contact_number': plant.plant_contact_number,
                'plant_account_number': plant.plant_account_number,
                'plant_company_name': plant.plant_company_name,
                'cloud_cover': plant.cloud_cover,
                'plant_area': plant.plant_area,
                'division': plant.division,
                'plant_account_type': plant.plant_account_type
            })
        elif request.method == 'PUT':
            data = request.json
            for key, value in data.items():
                setattr(plant, key, value)
            session.commit()
            return jsonify({"message": "Plant updated successfully"})
    finally:
        session.close()