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

    schedule.every(7).days.at("16:00").do(automatic_reserve_handler.notify_users)
    schedule.every(7).days.at("18:00").do(automatic_reserve_handler.handle_automatic_reserve)

    automatic_reserve_handler.automatic_reserve()
    while True:
        schedule.run_pending()
        time.sleep(60 * 60 * 24)