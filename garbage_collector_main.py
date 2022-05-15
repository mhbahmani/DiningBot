from src.utils import seprate_admins
from decouple import config
from garbage_collector import GarbageCollector
from src.db import DB

import schedule
import time


def update_user_records():
    garbage_collector.update_user_records()
    garbage_collector.update_ranks()

def clear_forget_codes():
    garbage_collector.clear_forget_codes()


garbage_collector = GarbageCollector(
        token=config('TOKEN'), 
        admin_ids=seprate_admins(config('ADMIN_ID')),
        log_level=config('LOG_LEVEL', default='INFO'),
        db=DB(
            host=config('DB_HOST', default='127.0.0.1'),
            port=config('DB_PORT', default='27017')
        ),
    )

schedule.every().day.at("22:00").do(update_user_records)
schedule.every().day.at("01:00").do(update_user_records)
schedule.every().day.at("02:00").do(update_user_records)
schedule.every().day.at("02:30").do(update_user_records)
schedule.every().day.at("03:00").do(update_user_records)
schedule.every().day.at("03:30").do(update_user_records)
schedule.every().day.at("04:00").do(update_user_records)
schedule.every().day.at("04:30").do(update_user_records)
schedule.every().day.at("05:00").do(update_user_records)
schedule.every().day.at("05:30").do(update_user_records)
schedule.every().day.at("06:00").do(update_user_records)
schedule.every().day.at("06:30").do(update_user_records)
schedule.every().day.at("06:45").do(update_user_records)
schedule.every().day.at("07:00").do(update_user_records)
schedule.every().day.at("07:15").do(update_user_records)
schedule.every().day.at("07:30").do(update_user_records)
schedule.every().day.at("07:45").do(update_user_records)
schedule.every().day.at("08:00").do(update_user_records)
schedule.every().day.at("08:15").do(update_user_records)
schedule.every().day.at("08:30").do(update_user_records)
schedule.every().day.at("08:45").do(update_user_records)
schedule.every().day.at("09:00").do(update_user_records)
schedule.every().day.at("09:30").do(update_user_records)
schedule.every().day.at("10:00").do(update_user_records)
schedule.every().day.at("10:30").do(update_user_records)
schedule.every().day.at("11:00").do(update_user_records)
schedule.every().day.at("11:30").do(update_user_records)
schedule.every().day.at("12:00").do(update_user_records)
schedule.every().day.at("12:30").do(update_user_records)

schedule.every().day.at("14:00").do(clear_forget_codes)

while True:
    garbage_collector.update_user_records()
    garbage_collector.update_ranks()
    schedule.run_pending()
    time.sleep(60 * 60)