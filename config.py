import os
#from dotenv import load_dotenv

#load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '11541514185144'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://') or 'sqlite:///solar_forecast.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SOLCAST_API_KEY = os.environ.get('SOLCAST_API_KEY') or 'your-solcast-api-key'
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')


    # Flask-Security config
    SECURITY_PASSWORD_SALT = 'your-password-salt'
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_UNAUTHORIZED_VIEW = None
    SECURITY_RECOVERABLE = True
    SECURITY_RESET_PASSWORD_WITHIN = '5 days'  # User has 5 days to reset password

    