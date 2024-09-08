from flask_security import RegisterForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf import FlaskForm

class ExtendedRegisterForm(RegisterForm):
    first_name = StringField('First Name', [DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', [DataRequired(), Length(max=100)])
    company = StringField('Company', [DataRequired(), Length(max=255)])
    designation = StringField('Designation', [DataRequired(), Length(max=255)])
    phone_number = StringField('Phone Number', [Optional(), Length(max=20)])





class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    company = StringField('Company', validators=[DataRequired(), Length(max=255)])
    designation = StringField('Designation', validators=[DataRequired(), Length(max=255)])
    phone_number = StringField('Phone Number', validators=[Optional(), Length(max=20)])