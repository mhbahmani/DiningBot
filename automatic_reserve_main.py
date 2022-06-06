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

    schedule.every().tuesday.at("10:00").do(automatic_reserve_handler.clean_reservation_status)

    schedule.every().tuesday.at("13:00").do(automatic_reserve_handler.notify_users)
    schedule.every().tuesday.at("15:00").do(automatic_reserve_handler.handle_automatic_reserve)
    schedule.every().wednesday.at("13:00").do(automatic_reserve_handler.notify_users)
    schedule.every().wednesday.at("15:00").do(automatic_reserve_handler.handle_automatic_reserve)
    schedule.every().wednesday.at("16:30").do(automatic_reserve_handler.notify_users_about_reservation_status)

    while True:
        schedule.run_pending()
        time.sleep(60 * 60)