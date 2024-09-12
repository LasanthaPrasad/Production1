from flask_wtf import FlaskForm
#from wtforms import StringField, PasswordField, BooleanField, SubmitField
#from wtforms.validators import DataRequired, Email, EqualTo, Length
from .models import User
from wtforms import StringField, FloatField, SelectField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Email, EqualTo, Length,  ValidationError


FORECAST_PROVIDERS = [
    ('solcast', 'Solcast'),
    #('visualcrossing', 'Visual Crossing'),
    ('geoclipz', 'GeoClipz Forecast'),
    #('openweather', 'OpenWeather')
    ]




class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class ForecastLocationForm(FlaskForm):
    provider_name = SelectField('Provider Name', choices=FORECAST_PROVIDERS, validators=[DataRequired()])
    latitude = FloatField('Latitude', validators=[DataRequired(), NumberRange(min=-90, max=90)])
    longitude = FloatField('Longitude', validators=[DataRequired(), NumberRange(min=-180, max=180)])
    api_key = StringField('API Key')

