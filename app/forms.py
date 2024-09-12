from flask_wtf import FlaskForm
#from wtforms import StringField, PasswordField, BooleanField, SubmitField
#from wtforms.validators import DataRequired, Email, EqualTo, Length
from .models import User
from wtforms import StringField, FloatField, SelectField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Email, EqualTo, Length,  ValidationError
import re

FORECAST_PROVIDERS = [
    ('solcast', 'Solcast'),
    #('visualcrossing', 'Visual Crossing'),
    ('geoclipz', 'GeoClipz Forecast'),
    #('openweather', 'OpenWeather')
    ]




def password_check(form, field):
    password = field.data
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    if not re.search("[a-z]", password):
        raise ValidationError('Password must contain at least one lowercase letter.')
    if not re.search("[A-Z]", password):
        raise ValidationError('Password must contain at least one uppercase letter.')
    if not re.search("[0-9]", password):
        raise ValidationError('Password must contain at least one number.')
    if not re.search("[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValidationError('Password must contain at least one special character.')

""" class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8), password_check])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one.')
       """  

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
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

