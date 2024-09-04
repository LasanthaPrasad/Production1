from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from app.models import SolarPlant, GridSubstation, Feeder, ForecastLocation








#@app.route('/')
#def index():
#    total_mw = db.session.query(db.func.sum(SolarPlant.installed_capacity)).scalar() or 0
#    total_capacity = db.session.query(db.func.sum(GridSubstation.installed_solar_capacity)).scalar() or 0
#    return render_template('index.html', total_mw=total_mw, total_capacity=total_capacity)


@app.route('/')
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
@app.route('/forecast_locations')
def forecast_locations():
    locations = ForecastLocation.query.all()
    return render_template('forecast_locations.html', locations=locations)

@app.route('/forecast_locations/create', methods=['GET', 'POST'])
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
        return redirect(url_for('forecast_locations'))
    return render_template('create_forecast_location.html')

@app.route('/forecast_locations/<int:id>/edit', methods=['GET', 'POST'])
def edit_forecast_location(id):
    location = ForecastLocation.query.get_or_404(id)
    if request.method == 'POST':
        location.provider_name = request.form['provider_name']
        location.latitude = float(request.form['latitude'])
        location.longitude = float(request.form['longitude'])
        db.session.commit()
        flash('Forecast Location updated successfully!', 'success')
        return redirect(url_for('forecast_locations'))
    return render_template('edit_forecast_location.html', location=location)

@app.route('/forecast_locations/<int:id>/delete', methods=['POST'])
def delete_forecast_location(id):
    location = ForecastLocation.query.get_or_404(id)
    db.session.delete(location)
    db.session.commit()
    flash('Forecast Location deleted successfully!', 'success')
    return redirect(url_for('forecast_locations'))

# Grid Substations
@app.route('/grid_substations')
def grid_substations():
    substations = GridSubstation.query.all()
    return render_template('grid_substations.html', substations=substations)



@app.route('/grid_substations/create', methods=['GET', 'POST'])
def create_grid_substation():
    if request.method == 'POST':
        substation = GridSubstation(
            name=request.form['name'],
            code=request.form['code'],
            latitude=float(request.form['latitude']),
            longitude=float(request.form['longitude']),
            installed_solar_capacity=float(request.form['installed_solar_capacity'])
        )
        db.session.add(substation)
        db.session.commit()
        flash('Grid Substation created successfully!', 'success')
        return redirect(url_for('grid_substations'))
    return render_template('create_grid_substation.html')

@app.route('/grid_substations/<int:id>/edit', methods=['GET', 'POST'])
def edit_grid_substation(id):
    substation = GridSubstation.query.get_or_404(id)
    if request.method == 'POST':
        substation.name = request.form['name']
        substation.code = request.form['code']
        substation.latitude = float(request.form['latitude'])
        substation.longitude = float(request.form['longitude'])
        substation.installed_solar_capacity = float(request.form['installed_solar_capacity'])
        db.session.commit()
        flash('Grid Substation updated successfully!', 'success')
        return redirect(url_for('grid_substations'))
    return render_template('edit_grid_substation.html', substation=substation)

@app.route('/grid_substations/<int:id>/delete', methods=['POST'])
def delete_grid_substation(id):
    substation = GridSubstation.query.get_or_404(id)
    db.session.delete(substation)
    db.session.commit()
    flash('Grid Substation deleted successfully!', 'success')
    return redirect(url_for('grid_substations'))

# Feeders
@app.route('/feeders')
def feeders():
    feeders = Feeder.query.options(db.joinedload(Feeder.grid_substation_rel)).all()
    return render_template('feeders.html', feeders=feeders)
#@app.route('/feeders')
#def feeders():
#    feeders = Feeder.query.all()
#    return render_template('feeders.html', feeders=feeders)

@app.route('/feeders/create', methods=['GET', 'POST'])
def create_feeder():
    if request.method == 'POST':
        feeder = Feeder(
            name=request.form['name'],
            code=request.form['code'],
            grid_substation=int(request.form['grid_substation']),
            installed_solar_capacity=float(request.form['installed_solar_capacity']),
            status=request.form['status']
        )
        db.session.add(feeder)
        db.session.commit()
        flash('Feeder created successfully!', 'success')
        return redirect(url_for('feeders'))
    substations = GridSubstation.query.all()
    return render_template('create_feeder.html', substations=substations)

@app.route('/feeders/<int:id>/edit', methods=['GET', 'POST'])
def edit_feeder(id):
    feeder = Feeder.query.get_or_404(id)
    if request.method == 'POST':
        feeder.name = request.form['name']
        feeder.code = request.form['code']
        feeder.grid_substation = int(request.form['grid_substation'])
        feeder.installed_solar_capacity = float(request.form['installed_solar_capacity'])
        feeder.status = request.form['status']
        db.session.commit()
        flash('Feeder updated successfully!', 'success')
        return redirect(url_for('feeders'))
    substations = GridSubstation.query.all()
    return render_template('edit_feeder.html', feeder=feeder, substations=substations)














@app.route('/feeders/<int:id>/delete', methods=['POST'])
def delete_feeder(id):
    feeder = Feeder.query.get_or_404(id)
    db.session.delete(feeder)
    db.session.commit()
    flash('Feeder deleted successfully!', 'success')
    return redirect(url_for('feeders'))


@app.route('/solar_plants')
def solar_plants():
    plants = SolarPlant.query.options(db.joinedload(SolarPlant.grid_substation_rel), 
                                      db.joinedload(SolarPlant.feeder_rel)).all()
    return render_template('solar_plants.html', plants=plants)

# Solar Plants
#@app.route('/solar_plants')
#def solar_plants():
#    plants = SolarPlant.query.all()
#    return render_template('solar_plants.html', plants=plants)


@app.route('/solar_plants/create', methods=['GET', 'POST'])
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
                company=request.form['company']
            )
            db.session.add(plant)
            db.session.commit()
            flash('Solar Plant created successfully!', 'success')
            return redirect(url_for('solar_plants'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating Solar Plant: {str(e)}', 'danger')

    substations = GridSubstation.query.all()
    forecast_locations = ForecastLocation.query.all()
    return render_template('create_solar_plant.html', substations=substations, forecast_locations=forecast_locations)

@app.route('/solar_plants/<int:id>/edit', methods=['GET', 'POST'])
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
            db.session.commit()
            flash('Solar Plant updated successfully!', 'success')
            return redirect(url_for('solar_plants'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating Solar Plant: {str(e)}', 'danger')

    substations = GridSubstation.query.all()
    forecast_locations = ForecastLocation.query.all()
    return render_template('edit_solar_plant.html', plant=plant, substations=substations, forecast_locations=forecast_locations)

@app.route('/get_feeders/<int:substation_id>')
def get_feeders(substation_id):
    feeders = Feeder.query.filter_by(grid_substation=substation_id).all()
    return jsonify([{'id': f.id, 'name': f.name} for f in feeders])


@app.route('/solar_plants/<int:id>/delete', methods=['POST'])
def delete_solar_plant(id):
    plant = SolarPlant.query.get_or_404(id)
    db.session.delete(plant)
    db.session.commit()
    flash('Solar Plant deleted successfully!', 'success')
    return redirect(url_for('solar_plants'))