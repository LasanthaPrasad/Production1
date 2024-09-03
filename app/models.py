from app import db

class SolarPlant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    grid_substation_id = db.Column(db.Integer, db.ForeignKey('gridsubstation.id'), nullable=False)
    feeder_id = db.Column(db.Integer, db.ForeignKey('feeder.id'), nullable=False)
    forecast_location_id = db.Column(db.Integer, db.ForeignKey('forecastlocation.id'), nullable=False)
    installed_capacity = db.Column(db.Float, nullable=False)
    panel_capacity = db.Column(db.Float, nullable=False)
    inverter_capacity = db.Column(db.Float, nullable=False)
    plant_angle = db.Column(db.Float, nullable=False)
    company = db.Column(db.String(100), nullable=False)

class GridSubstation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    forecast_location_id = db.Column(db.Integer, db.ForeignKey('forecastlocation.id'), nullable=False)
    installed_solar_capacity = db.Column(db.Float, nullable=False)

class Feeder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    grid_substation_id = db.Column(db.Integer, db.ForeignKey('gridsubstation.id'), nullable=False)
    installed_solar_capacity = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    outage_start = db.Column(db.DateTime)
    outage_end = db.Column(db.DateTime)

class ForecastLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    ghi = db.Column(db.Float, nullable=False)
    dni = db.Column(db.Float, nullable=False)
    dhi = db.Column(db.Float, nullable=False)
    air_temperature = db.Column(db.Float, nullable=False)
    zenith = db.Column(db.Float, nullable=False)
    azimuth = db.Column(db.Float, nullable=False)
    cloud_opacity = db.Column(db.Float, nullable=False)
    next_hour_forecast = db.Column(db.JSON, nullable=False)
    next_24_hours_forecast = db.Column(db.JSON, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'provider_name': self.provider_name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'ghi': self.ghi,
            'dni': self.dni,
            'dhi': self.dhi,
            'air_temperature': self.air_temperature,
            'zenith': self.zenith,
            'azimuth': self.azimuth,
            'cloud_opacity': self.cloud_opacity,
            'next_hour_forecast': self.next_hour_forecast,
            'next_24_hours_forecast': self.next_24_hours_forecast
        }