import schedule
import time
from core.storage import init_db
from main import run_scraper   # run_scraper now lives only in main.py

init_db()
run_scraper()  # Run once immediately on start

schedule.every(30).minutes.do(run_scraper)

while True:
    schedule.run_pending()
    time.sleep(60)