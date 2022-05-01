from src.utils import seprate_admins
from decouple import config
from src.app import DiningBot


DiningBot(
    config('TOKEN'), 
    seprate_admins(config('ADMIN_ID')),
    config('LOG_LEVEL', default='INFO')
    ).run()