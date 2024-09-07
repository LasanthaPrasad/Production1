
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from . import db
from .models import ForecastLocation, IrradiationForecast, SolarPlant, GridSubstation, Feeder
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import joinedload
import uuid
from .auth import require_api_key


main = Blueprint('main', __name__)

@main.route('/solar_plants/<int:id>/generate_api_key', methods=['POST'])
def generate_solar_plant_api_key(id):
    plant = SolarPlant.query.get_or_404(id)
    plant.api_key = str(uuid.uuid4())
    db.session.commit()
    flash('New API key generated for Solar Plant', 'success')
    return redirect(url_for('main.solar_plants'))

@main.route('/grid_substations/<int:id>/generate_api_key', methods=['POST'])
def generate_grid_substation_api_key(id):
    substation = GridSubstation.query.get_or_404(id)
    substation.api_key = str(uuid.uuid4())
    db.session.commit()
    flash('New API key generated for Grid Substation', 'success')
    return redirect(url_for('main.grid_substations'))





@main.route('/api/plant_forecast')
@require_api_key
def get_plant_forecast(plant_id):
    plant = SolarPlant.query.get_or_404(plant_id)
    forecasts = calculate_plant_forecasts(plant)
    return jsonify(forecasts)


def calculate_plant_forecasts(plant):
        
        now = datetime.now(timezone.utc)
        three_days_later = now + timedelta(days=1)


        forecasts = IrradiationForecast.query.filter_by(forecast_location_id=plant.forecast_location).filter(            
            IrradiationForecast.timestamp >= now,
            IrradiationForecast.timestamp <= three_days_later
        ).order_by(IrradiationForecast.timestamp).all()




        if not forecasts:
            return jsonify({'error': 'No forecast data available'}), 404



        plant_forecasts = []
        for forecast in forecasts:
        # This is a simplified calculation. You might need a more complex model.
            estimated_mw = (forecast.ghi / 150) * plant.installed_capacity * 0.15  # Assuming 15% efficiency
            plant_forecasts.append({
            'timestamp': forecast.timestamp.isoformat(),
            'estimated_mw': estimated_mw
        })

        return plant_forecasts



@main.route('/api/plant_forecast/<int:plant_id>')
def get_plant_forecast1(plant_id):
    plant = SolarPlant.query.get_or_404(plant_id)
    forecasts = calculate_plant_forecasts(plant)
    return jsonify(forecasts)


@main.route('/api/check_forecasts/<int:location_id>')
def check_forecasts(location_id):

    now = datetime.now(timezone.utc)
    three_days_later = now + timedelta(days=1)
        
    forecasts = IrradiationForecast.query.filter(
            IrradiationForecast.forecast_location_id == location_id,
            IrradiationForecast.timestamp >= now,
            IrradiationForecast.timestamp <= three_days_later
        ).order_by(IrradiationForecast.timestamp).all()



    #forecasts = IrradiationForecast.query.filter_by(forecast_location_id=location_id).limit(100).all()
    return jsonify([{
        'timestamp': f.timestamp.isoformat(),
        'ghi': f.ghi,
        'dni': f.dni,
        'dhi': f.dhi
    } for f in forecasts])



@main.route('/api/location_forecast/<int:location_id>')
def get_location_forecast(location_id):
    try:
        now = datetime.now(timezone.utc)
        three_days_later = now + timedelta(days=1)
        
        forecasts = IrradiationForecast.query.filter(
            IrradiationForecast.forecast_location_id == location_id,
            IrradiationForecast.timestamp >= now,
            IrradiationForecast.timestamp <= three_days_later
        ).order_by(IrradiationForecast.timestamp).all()

        if not forecasts:
            return jsonify({'error': 'No forecast data available'}), 404

        timestamps = [f.timestamp.isoformat() for f in forecasts]
        ghi_values = [f.ghi for f in forecasts]
        dni_values = [f.dni for f in forecasts]
        dhi_values = [f.dhi for f in forecasts]

        return jsonify({
            'timestamps': timestamps,
            'ghi': ghi_values,
            'dni': dni_values,
            'dhi': dhi_values
        })
    except Exception as e:
        print(f"Error in get_location_forecast: {str(e)}")  # Server-side logging
        return jsonify({'error': str(e)}), 500







def recalculate_all_substation_capacities():
    substations = GridSubstation.query.all()
    for substation in substations:
        substation.update_installed_capacity()
    db.session.commit()



#@app.route('/')
#def index():
#    total_mw = db.session.query(db.func.sum(SolarPlant.installed_capacity)).scalar() or 0
#    total_capacity = db.session.query(db.func.sum(GridSubstation.installed_solar_capacity)).scalar() or 0
#    return render_template('index.html', total_mw=total_mw, total_capacity=total_capacity)


@main.route('/')
def index():
    total_mw = db.session.query(db.func.sum(SolarPlant.installed_capacity)).scalar() or 0
    total_capacity = db.session.query(db.func.sum(GridSubstation.installed_solar_capacity)).scalar() or 0
    forecast_locations = ForecastLocation.query.all()
    
    # Add this print statement for debugging
    print(f"Number of forecast locations: {len(forecast_locations)}")
    
    return render_template('index.html', 
                           total_mw=total_mw, 
                           total_capacity=total_capacity,
                           forecast_locations=forecast_locations)







# Forecast Locations
@main.route('/forecast_locations')
def forecast_locations():
    locations = ForecastLocation.query.all()
    return render_template('forecast_locations.html', locations=locations)




@main.route('/forecast_locations/create', methods=['GET', 'POST'])
def create_forecast_location():
    if request.method == 'POST':
        location = ForecastLocation(
            provider_name=request.form['provider_name'],
            latitude=float(request.form['latitude']),
            longitude=float(request.form['longitude'])
        )
        db.session.add(location)
        db.session.commit()
        flash('Forecast Location created successfully!', 'success')
        return redirect(url_for('main.forecast_locations'))
    return render_template('create_forecast_location.html')


@main.route('/forecast_locations/<int:id>/edit', methods=['GET', 'POST'])
def edit_forecast_location(id):
    location = ForecastLocation.query.get_or_404(id)
    if request.method == 'POST':
        location.provider_name = request.form['provider_name']
        location.latitude = float(request.form['latitude'])
        location.longitude = float(request.form['longitude'])
        db.session.commit()
        flash('Forecast Location updated successfully!', 'success')
        return redirect(url_for('main.forecast_locations'))
    return render_template('edit_forecast_location.html', location=location)

@main.route('/forecast_locations/<int:id>/delete', methods=['POST'])
def delete_forecast_location(id):
    location = ForecastLocation.query.get_or_404(id)
    db.session.delete(location)
    db.session.commit()
    flash('Forecast Location deleted successfully!', 'success')
    return redirect(url_for('main.forecast_locations'))

# Grid Substations
@main.route('/grid_substations')
def grid_substations():
    substations = GridSubstation.query.all()
    return render_template('grid_substations.html', substations=substations)



@main.route('/grid_substations/create', methods=['GET', 'POST'])
def create_grid_substation():
    if request.method == 'POST':
        substation = GridSubstation(
            name=request.form['name'],
            code=request.form['code'],
            latitude=float(request.form['latitude']),
            longitude=float(request.form['longitude']),
            installed_solar_capacity=float(request.form['installed_solar_capacity']),
            api_status=request.form['api_status']
        )
        db.session.add(substation)
        db.session.commit()
        flash('Grid Substation created successfully!', 'success')
        return redirect(url_for('main.grid_substations'))
    return render_template('create_grid_substation.html')

@main.route('/grid_substations/<int:id>/edit', methods=['GET', 'POST'])
def edit_grid_substation(id):
    substation = GridSubstation.query.get_or_404(id)
    if request.method == 'POST':
        substation.name = request.form['name']
        substation.code = request.form['code']
        substation.latitude = float(request.form['latitude'])
        substation.longitude = float(request.form['longitude'])
        substation.installed_solar_capacity = float(request.form['installed_solar_capacity'])
        substation.api_status=request.form['api_status']
        db.session.commit()
        flash('Grid Substation updated successfully!', 'success')
        return redirect(url_for('main.grid_substations'))
    return render_template('edit_grid_substation.html', substation=substation)

@main.route('/grid_substations/<int:id>/delete', methods=['POST'])
def delete_grid_substation(id):
    substation = GridSubstation.query.get_or_404(id)
    db.session.delete(substation)
    db.session.commit()
    flash('Grid Substation deleted successfully!', 'success')
    return redirect(url_for('main.grid_substations'))



@main.route('/feeders/create', methods=['GET', 'POST'])
def create_feeder():
    if request.method == 'POST':
        try:
            feeder = Feeder(
                name=request.form['name'],
                code=request.form['code'],
                grid_substation=int(request.form['grid_substation']),
                installed_solar_capacity=float(request.form['installed_solar_capacity']),
                status=request.form['status']
            )
            db.session.add(feeder)
            db.session.commit()
            
            # Update Grid Substation capacity
            substation = GridSubstation.query.get(feeder.grid_substation)
            substation.update_installed_capacity()
            
            flash('Feeder created successfully!', 'success')
            return redirect(url_for('main.feeders'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating Feeder: {str(e)}', 'danger')

    substations = GridSubstation.query.all()
    return render_template('create_feeder.html', substations=substations)

@main.route('/feeders/<int:id>/edit', methods=['GET', 'POST'])
def edit_feeder(id):
    feeder = Feeder.query.get_or_404(id)
    old_status = feeder.status
    old_substation_id = feeder.grid_substation

    if request.method == 'POST':
        try:
            feeder.name = request.form['name']
            feeder.code = request.form['code']
            feeder.grid_substation = int(request.form['grid_substation'])
            feeder.installed_solar_capacity = float(request.form['installed_solar_capacity'])
            feeder.status = request.form['status']
            db.session.commit()
            
            # Update old Grid Substation capacity if changed
            if old_substation_id != feeder.grid_substation or old_status != feeder.status:
                old_substation = GridSubstation.query.get(old_substation_id)
                old_substation.update_installed_capacity()
            
            # Update new Grid Substation capacity
            new_substation = GridSubstation.query.get(feeder.grid_substation)
            new_substation.update_installed_capacity()
            
            flash('Feeder updated successfully!', 'success')
            return redirect(url_for('main.feeders'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating Feeder: {str(e)}', 'danger')

    substations = GridSubstation.query.all()
    return render_template('edit_feeder.html', feeder=feeder, substations=substations)

@main.route('/feeders/<int:id>/delete', methods=['POST'])
def delete_feeder(id):
    feeder = Feeder.query.get_or_404(id)
    try:
        substation = GridSubstation.query.get(feeder.grid_substation)
        db.session.delete(feeder)
        db.session.commit()
        
        # Update Grid Substation capacity
        substation.update_installed_capacity()
        
        flash('Feeder deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting Feeder: {str(e)}', 'danger')
    return redirect(url_for('main.feeders'))





# Feeders
@main.route('/feeders')
def feeders():
    feeders = Feeder.query.options(db.joinedload(Feeder.grid_substation_rel)).all()
    return render_template('feeders.html', feeders=feeders)
#@app.route('/feeders')
#def feeders():
#    feeders = Feeder.query.all()
#    return render_template('feeders.html', feeders=feeders)


#@main.route('/solar_plants')
#def solar_plants():
#   plants = SolarPlant.query.options(db.joinedload(SolarPlant.grid_substation_rel), 
#                                      db.joinedload(SolarPlant.feeder_rel)).all()
#    return render_template('solar_plants.html', plants=plants)


@main.route('/solar_plants')
def solar_plants():
    plants = SolarPlant.query.options(
        joinedload(SolarPlant.grid_substation_rel),
        joinedload(SolarPlant.feeder_rel)
    ).all()
    return render_template('solar_plants.html', plants=plants)

# Solar Plants
#@app.route('/solar_plants')
#def solar_plants():
#    plants = SolarPlant.query.all()
#    return render_template('solar_plants.html', plants=plants)


@main.route('/solar_plants/create', methods=['GET', 'POST'])
def create_solar_plant():
    if request.method == 'POST':
        try:
            plant = SolarPlant(
                name=request.form['name'],
                latitude=float(request.form['latitude']),
                longitude=float(request.form['longitude']),
                grid_substation=int(request.form['grid_substation']),
                feeder=int(request.form['feeder']),
                forecast_location=int(request.form['forecast_location']),
                installed_capacity=float(request.form['installed_capacity']),
                panel_capacity=float(request.form['panel_capacity']),
                inverter_capacity=float(request.form['inverter_capacity']),
                plant_angle=float(request.form['plant_angle']),
                company=request.form['company'],
                api_status=request.form['api_status']
            )
            db.session.add(plant)
            db.session.commit()
            flash('Solar Plant created successfully!', 'success')
            return redirect(url_for('main.solar_plants'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating Solar Plant: {str(e)}', 'danger')

    substations = GridSubstation.query.all()
    forecast_locations = ForecastLocation.query.all()
    return render_template('create_solar_plant.html', substations=substations, forecast_locations=forecast_locations)

@main.route('/solar_plants/<int:id>/edit', methods=['GET', 'POST'])
def edit_solar_plant(id):
    plant = SolarPlant.query.get_or_404(id)
    if request.method == 'POST':
        try:
            plant.name = request.form['name']
            plant.latitude = float(request.form['latitude'])
            plant.longitude = float(request.form['longitude'])
            plant.grid_substation = int(request.form['grid_substation'])
            plant.feeder = int(request.form['feeder'])
            plant.forecast_location = int(request.form['forecast_location'])
            plant.installed_capacity = float(request.form['installed_capacity'])
            plant.panel_capacity = float(request.form['panel_capacity'])
            plant.inverter_capacity = float(request.form['inverter_capacity'])
            plant.plant_angle = float(request.form['plant_angle'])
            plant.company = request.form['company']
            plant.api_status = request.form['api_status']           
            db.session.commit()
            flash('Solar Plant updated successfully!', 'success')
            return redirect(url_for('main.solar_plants'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating Solar Plant: {str(e)}', 'danger')

    substations = GridSubstation.query.all()
    forecast_locations = ForecastLocation.query.all()
    return render_template('edit_solar_plant.html', plant=plant, substations=substations, forecast_locations=forecast_locations)

@main.route('/get_feeders/<int:substation_id>')
def get_feeders(substation_id):
    feeders = Feeder.query.filter_by(grid_substation=substation_id).all()
    return jsonify([{'id': f.id, 'name': f.name} for f in feeders])


@main.route('/solar_plants/<int:id>/delete', methods=['POST'])
def delete_solar_plant(id):
    plant = SolarPlant.query.get_or_404(id)
    db.session.delete(plant)
    db.session.commit()
    flash('Solar Plant deleted successfully!', 'success')
    return redirect(url_for('main.solar_plants'))


