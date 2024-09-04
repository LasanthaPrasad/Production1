from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from app import routes, models


from apscheduler.schedulers.background import BackgroundScheduler
from app.solcast_api import fetch_solcast_forecasts

scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_solcast_forecasts, trigger="interval", hours=1)
scheduler.start()