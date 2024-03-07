from src.utils import seprate_admins
from decouple import config
from src.app import DiningBot
from src.db import DB


DiningBot(
    token=config('TOKEN'), 
    admin_ids=seprate_admins(config('ADMIN_ID')),
    log_level=config('LOG_LEVEL', default='INFO'),
    log_file_path=config('LOG_FILE_PATH', default='dining-bot.log'),
    db=DB(
        host=config('DB_HOST', default='127.0.0.1'),
        port=config('DB_PORT', default='27017')
    ),
    admin_sso_username=config('ADMIN_SHARIF_SSO_USERNAME'),
    admin_sso_password=config('ADMIN_SHARIF_SSO_PASSWORD'),
    sentry_dsn=config('SENTRY_DSN', default=None),
    environment=config('ENVIRONMENT', default='development'),
).run()
