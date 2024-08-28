#from flask import Flask
#from flask_sqlalchemy import SQLAlchemy
#from apscheduler.schedulers.background import BackgroundScheduler
#from config import Config

#db = SQLAlchemy()
#scheduler = BackgroundScheduler()

#def create_app():
 #   app = Flask(__name__)
 #   app.config.from_object(Config)
#
 #   db.init_app(app)

#    from app import routes
 #   app.register_blueprint(routes.main)

 #   from app.utils import fetch_solar_forecast, fetch_wind_forecast, fetch_hydro_forecast
 #   scheduler.add_job(fetch_solar_forecast, 'interval', hours=1, args=[app])
 #   scheduler.add_job(fetch_wind_forecast, 'interval', hours=1, args=[app])
#    scheduler.add_job(fetch_hydro_forecast, 'interval', hours=1, args=[app])
 #   scheduler.start()

#    return app
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config

scheduler = BackgroundScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from app import routes
    app.register_blueprint(routes.main)

    return app