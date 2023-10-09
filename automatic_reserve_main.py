from src.utils import seprate_admins
from decouple import config
from src.automatic_reserve_handler import AutomaticReserveHandler
from src.db import DB

# import schedule
import asyncio

import asyncio
import aioschedule as schedule
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

    schedule.every().monday.at("10:00").do(automatic_reserve_handler.clean_reservation_status)

    schedule.every().monday.at("14:00").do(automatic_reserve_handler.notify_users)
    schedule.every().monday.at("16:00").do(automatic_reserve_handler.handle_automatic_reserve)
    schedule.every().tuesday.at("14:00").do(automatic_reserve_handler.notify_users)
    schedule.every().tuesday.at("16:00").do(automatic_reserve_handler.handle_automatic_reserve)
    schedule.every().wednesday.at("14:00").do(automatic_reserve_handler.notify_users)
    schedule.every().wednesday.at("16:00").do(automatic_reserve_handler.handle_automatic_reserve)
    schedule.every().wednesday.at("17:30").do(automatic_reserve_handler.notify_users_about_reservation_status)

    loop = asyncio.get_event_loop()
    while True:
        loop.run_until_complete(schedule.run_pending())
        time.sleep(1)