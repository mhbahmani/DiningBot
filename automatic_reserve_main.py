from src.utils import seprate_admins
from decouple import config
from src.automatic_reserve_handler import AutomaticReserveHandler
from src.db import DB

import schedule
import time


if __name__ == '__main__':
    automatic_reserve_handler = AutomaticReserveHandler(
            token=config('TOKEN'), 
            admin_ids=seprate_admins(config('ADMIN_ID')),
            log_level=config('LOG_LEVEL', default='INFO'),
            db=DB(
                host=config('DB_HOST', default='127.0.0.1'),
                port=config('DB_PORT', default='27017')
            ),
        )

    schedule.every().monday.at("16:00").do(automatic_reserve_handler.notify_users)
    schedule.every().monday.at("18:00").do(automatic_reserve_handler.handle_automatic_reserve)
    schedule.every().tuesday.at("16:00").do(automatic_reserve_handler.notify_users)
    schedule.every().tuesday.at("18:00").do(automatic_reserve_handler.handle_automatic_reserve)
    schedule.every().wednesday.at("16:00").do(automatic_reserve_handler.notify_users)
    schedule.every().wednesday.at("18:00").do(automatic_reserve_handler.handle_automatic_reserve)
    schedule.every().wednesday.at("18:30").do(automatic_reserve_handler.notify_users_about_reservation_status)

    automatic_reserve_handler.notify_users()
    time.sleep(60 * 2)
    automatic_reserve_handler.automatic_reserve()
    while True:
        schedule.run_pending()
        time.sleep(60 * 60)