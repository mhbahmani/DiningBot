from src.utils import seprate_admins
from decouple import config
from src.app import DiningBot
from src.garbage_collector import GarbageCollector
from src.db import DB


GarbageCollector(
    token=config('TOKEN'), 
    admin_ids=seprate_admins(config('ADMIN_ID')),
    log_level=config('LOG_LEVEL', default='INFO'),
    db=DB(
        host=config('DB_HOST', default='127.0.0.1'),
        port=config('DB_PORT', default='27017')
    ),
).run()