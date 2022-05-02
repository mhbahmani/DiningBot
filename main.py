from src.utils import seprate_admins
from decouple import config
from src.app import DiningBot
from src.db import DB


DiningBot(
    token=config('TOKEN'), 
    admins=seprate_admins(config('ADMIN_ID')),
    log_leve=config('LOG_LEVEL', default='INFO'),
    db=DB(
        host=config('DB_HOST', default='127.0.0.1'),
        port=config('DB_PORT', default='27017')
    )
).run()