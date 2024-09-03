from app import app
from app.routes import fetch_forecast
import schedule
import time

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)  # Wait for 1 minute before checking again

if __name__ == '__main__':
    schedule.every().hour.do(fetch_forecast)
    run_scheduler()