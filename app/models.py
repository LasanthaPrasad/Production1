from . import db
from datetime import datetime
import uuid
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(64))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)




class IrradiationForecast(db.Model):
    __tablename__ = 'irradiation_forecasts'
    id = db.Column(db.Integer, primary_key=True)
    forecast_location_id = db.Column(db.Integer, db.ForeignKey('forecast_locations.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    ghi = db.Column(db.Float)
    dni = db.Column(db.Float)
    dhi = db.Column(db.Float)
    air_temp = db.Column(db.Float)
    cloud_opacity = db.Column(db.Float)

    forecast_location = db.relationship('ForecastLocation', backref='irradiation_forecasts')

    __table_args__ = (db.UniqueConstraint('forecast_location_id', 'timestamp', name='uix_1'),)





class ForecastLocation(db.Model):
    __tablename__ = 'forecast_locations'
    id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)

    solcast_resource_id = db.Column(db.String(255), unique=True)

    ghi = db.Column(db.Numeric(10, 2))
    dni = db.Column(db.Numeric(10, 2))
    dhi = db.Column(db.Numeric(10, 2))
    air_temperature = db.Column(db.Numeric(5, 2))
    zenith = db.Column(db.Numeric(5, 2))
    azimuth = db.Column(db.Numeric(5, 2))
    cloud_opacity = db.Column(db.Numeric(5, 2))
    next_hour_forecast = db.Column(db.JSON)
    next_24_hours_forecast = db.Column(db.JSON)

class GridSubstation(db.Model):
    __tablename__ = 'grid_substations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)
    forecast_location = db.Column(db.Integer, db.ForeignKey('forecast_locations.id'))
    installed_solar_capacity = db.Column(db.Numeric(10, 2))
    api_key = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    api_status = db.Column(db.String(10), default='disabled')


    def update_installed_capacity(self):
        total_capacity = sum(feeder.installed_solar_capacity 
                             for feeder in self.feeders 
                             if feeder.status == 'active')
        self.installed_solar_capacity = total_capacity
        db.session.commit()
        
#class Feeder(db.Model):
#    __tablename__ = 'feeders'
#    id = db.Column(db.Integer, primary_key=True)
#    name = db.Column(db.String(255), nullable=False)
#    code = db.Column(db.String(50), unique=True, nullable=False)
#    grid_substation = db.Column(db.Integer, db.ForeignKey('grid_substations.id'))
#    installed_solar_capacity = db.Column(db.Numeric(10, 2))
#    status = db.Column(db.String(50))
#    outage_start = db.Column(db.DateTime)
#    outage_end = db.Column(db.DateTime)



class Feeder(db.Model):
    __tablename__ = 'feeders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    grid_substation = db.Column(db.Integer, db.ForeignKey('grid_substations.id'), nullable=False)
    installed_solar_capacity = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(50), default='active')
    outage_start = db.Column(db.DateTime)
    outage_end = db.Column(db.DateTime)

    grid_substation_rel = db.relationship('GridSubstation', backref='feeders')


class SolarPlant(db.Model):
    __tablename__ = 'solar_plants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    grid_substation = db.Column(db.Integer, db.ForeignKey('grid_substations.id'), nullable=False)
    feeder = db.Column(db.Integer, db.ForeignKey('feeders.id'), nullable=False)
    forecast_location = db.Column(db.Integer, db.ForeignKey('forecast_locations.id'), nullable=False)
    installed_capacity = db.Column(db.Float, nullable=False)
    panel_capacity = db.Column(db.Float, nullable=False)
    inverter_capacity = db.Column(db.Float, nullable=False)
    plant_angle = db.Column(db.Float, nullable=False)
    company = db.Column(db.String(255), nullable=False)
    api_key = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    api_status = db.Column(db.String(10), default='disabled')


    grid_substation_rel = db.relationship('GridSubstation', backref='solar_plants')
    feeder_rel = db.relationship('Feeder', backref='solar_plants')
    forecast_location_rel = db.relationship('ForecastLocation', backref='solar_plants')
#class SolarPlant(db.Model):
#    __tablename__ = 'solar_plants'
#    id = db.Column(db.Integer, primary_key=True)
#    name = db.Column(db.String(255), nullable=False)
#    latitude = db.Column(db.Numeric(10, 8), nullable=False)
#    longitude = db.Column(db.Numeric(11, 8), nullable=False)
#    grid_substation = db.Column(db.Integer, db.ForeignKey('grid_substations.id'))
#    feeder = db.Column(db.Integer, db.ForeignKey('feeders.id'))
#    forecast_location = db.Column(db.Integer, db.ForeignKey('forecast_locations.id'))
#    installed_capacity = db.Column(db.Numeric(10, 2))
#    panel_capacity = db.Column(db.Numeric(10, 2))
#    inverter_capacity = db.Column(db.Numeric(10, 2))
#    plant_angle = db.Column(db.Numeric(5, 2))
#    company = db.Column(db.String(255))

class Forecast(db.Model):
    __tablename__ = 'forecasts'
    id = db.Column(db.Integer, primary_key=True)
    solar_plant = db.Column(db.Integer, db.ForeignKey('solar_plants.id'))
    grid_substation = db.Column(db.Integer, db.ForeignKey('grid_substations.id'))
    forecast_location = db.Column(db.Integer, db.ForeignKey('forecast_locations.id'))
    forecast_timestamp = db.Column(db.DateTime, nullable=False)
    forecast_interval = db.Column(db.String(20))
    forecasted_mw = db.Column(db.JSON)