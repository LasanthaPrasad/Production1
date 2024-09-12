
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
#from . import db
from .models import ForecastLocation, IrradiationForecast, SolarPlant, GridSubstation, Feeder, User, Role
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import joinedload
import uuid
from .auth import require_api_key
from flask_security import login_required, roles_required, roles_accepted, current_user

from flask import render_template, redirect, url_for, request, flash

from flask_security.views import reset_password, forgot_password
from flask_security.utils import hash_password

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField
from wtforms.validators import DataRequired, NumberRange
from .forecast_service import ForecastService



#from config import FORECAST_PROVIDERS  # or from wherever you defined the providers

    # config.py or a new file like providers.py
FORECAST_PROVIDERS = [
    ('solcast', 'Solcast'),
    #('visualcrossing', 'Visual Crossing'),
    ('geoclipz', 'GeoClipz Forecast'),
    #('openweather', 'OpenWeather')
    ]

from .extensions import db, security
import string
import random




main = Blueprint('main', __name__)



class ForecastLocationForm(FlaskForm):
    provider_name = SelectField('Provider Name', choices=FORECAST_PROVIDERS, validators=[DataRequired()])
    latitude = FloatField('Latitude', validators=[DataRequired(), NumberRange(min=-90, max=90)])
    longitude = FloatField('Longitude', validators=[DataRequired(), NumberRange(min=-180, max=180)])
    api_key = StringField('API Key')

@main.route('/view_data')
@login_required
def view_data():
    # All logged in users can view this
    return render_template('view_data.html')

@main.route('/edit_data')
@roles_accepted('moderator', 'admin')
def edit_data():
    # Only moderators and admins can access this
    return render_template('edit_data.html')

@main.route('/manage_users')
#@roles_required('admin')
def manage_users():
    # Only admins can access this
    users = User.query.all()
    return render_template('manage_users.html', users=users)









@main.route('/toggle_user_status/<int:user_id>', methods=['POST'])
@roles_required('admin')
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    user.active = not user.active
    db.session.commit()
    status = 'activated' if user.active else 'deactivated'
    flash(f'User {user.email} has been {status}', 'success')
    return redirect(url_for('main.manage_users'))

@main.route('/reset_user_password/<int:user_id>', methods=['POST'])
@roles_required('admin')
def reset_user_password(user_id):
    user = User.query.get_or_404(user_id)
    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    user.password = hash_password(new_password)
    db.session.commit()
    
    # Here you would typically send an email to the user with their new password
    # For this example, we'll just flash it (not secure for production!)
    flash(f'Password for {user.email} has been reset. New password: {new_password}', 'success')
    return redirect(url_for('main.manage_users'))

# Update the existing change_user_role function
@main.route('/change_user_role/<int:user_id>', methods=['POST'])
@roles_required('admin')
def change_user_role(user_id):
    user_datastore = security.datastore
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    if new_role in ['user', 'moderator', 'admin']:
        # Remove all existing roles
        for role in user.roles:
            user_datastore.remove_role_from_user(user, role)
        # Add the new role
        role = Role.query.filter_by(name=new_role).first()
        if role:
            user_datastore.add_role_to_user(user, role)
            db.session.commit()
            flash(f'Role updated for user {user.email} to {new_role}', 'success')
        else:
            flash(f'Role {new_role} not found', 'error')
    else:
        flash(f'Invalid role specified', 'error')
    return redirect(url_for('main.manage_users'))






def init_routes(app):
    user_datastore = security.datastore

    @app.route('/reset', methods=['GET', 'POST'])
    def reset():
        return security.forgot_password_view()

    @app.route('/reset/<token>', methods=['GET', 'POST'])
    def reset_with_token(token):
        return security.reset_password_view(token)

    @app.route('/change-password', methods=['GET', 'POST'])
    @login_required
    def change_password():
        if request.method == 'POST':
            password = request.form.get('password')
            if password:
                current_user.password = hash_password(password)
                user_datastore.put(current_user)
                db.session.commit()
                flash('Password updated successfully.', 'success')
                return redirect(url_for('profile'))
        return render_template('change_password.html')



def init_app(app):
    init_routes(app)







#@main.route('/forgot-password', endpoint='security_forgot_password')
#def forgot_password():
#    return security_forgot_password()



@main.route('/profile')
@login_required
def profile():
    """User profile page route"""
    return render_template('profile.html', user=current_user)

@main.route('/admin')
@roles_required('admin')
def admin():
    """Admin dashboard route"""
    # Here you might want to fetch some admin-specific data
    return render_template('admin.html')

















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
        three_days_later = now + timedelta(days=3)
        
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
    form = ForecastLocationForm()
    if form.validate_on_submit():
        location = ForecastLocation(
            provider_name=form.provider_name.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            api_key=form.api_key.data
        )
        db.session.add(location)
        db.session.commit()


        forecast_service = ForecastService()
        try:
            forecast_service.fetch_and_save_forecasts(location)
            flash('Forecast location created and initial forecast data fetched successfully', 'success')
        except Exception as e:
            flash(f'Forecast location created, but failed to fetch initial forecast data: {str(e)}', 'warning')



        flash('Forecast location created successfully', 'success')
        return redirect(url_for('main.forecast_locations'))
    return render_template('create_forecast_location.html', form=form)

@main.route('/forecast_locations/<int:id>/edit', methods=['GET', 'POST'])
def edit_forecast_location(id):
    location = ForecastLocation.query.get_or_404(id)
    form = ForecastLocationForm(obj=location)
    if form.validate_on_submit():
        form.populate_obj(location)
        db.session.commit()
        forecast_service = ForecastService()
        try:
            forecast_service.fetch_and_save_forecasts(location)
            flash('Forecast location created and initial forecast data fetched successfully', 'success')
        except Exception as e:
            flash(f'Forecast location created, but failed to fetch initial forecast data: {str(e)}', 'warning')



        flash('Forecast location updated successfully', 'success')
        return redirect(url_for('main.forecast_locations'))
    return render_template('edit_forecast_location.html', form=form, location=location)





""" 
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
 """



""" 

@main.route('/forecast_locations/<int:id>/delete', methods=['POST'])
def delete_forecast_location(id):
    location = ForecastLocation.query.get_or_404(id)
    db.session.delete(location)
    db.session.commit()
    flash('Forecast Location deleted successfully!', 'success')
    return redirect(url_for('main.forecast_locations'))

 """

@main.route('/forecast_locations/<int:location_id>/delete', methods=['POST'])
def delete_forecast_location(location_id):
    location = ForecastLocation.query.get_or_404(location_id)
    try:
        # First, delete all associated irradiation forecasts
        IrradiationForecast.query.filter_by(forecast_location_id=location_id).delete()
        
        # Then delete the forecast location
        db.session.delete(location)
        db.session.commit()
        flash('Forecast location and associated forecasts deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting forecast location: {str(e)}', 'error')
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
    forecast_locations = ForecastLocation.query.all()
    return render_template('create_grid_substation.html', forecast_locations=forecast_locations)



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

    forecast_locations = ForecastLocation.query.all()
    return render_template('edit_grid_substation.html', substation=substation, forecast_locations=forecast_locations)

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


