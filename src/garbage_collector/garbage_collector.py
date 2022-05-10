import logging
from telegram.ext import Updater
from src.db import DB


class GarbageCollector:
    def __init__(self, token = None, admin_ids=set(), log_level='INFO', db: DB = None):
        if token:
            self.updater = Updater(token=token, use_context=True)
            self.dispatcher = self.updater.dispatcher
        self.db = db
        self.admin_ids = admin_ids
        logging.basicConfig(
            format='%(asctime)s - %(levelname)s - %(message)s',
            level={
                'INFO': logging.INFO,
                'DEBUG': logging.DEBUG,
                'ERROR': logging.ERROR,
            }[log_level])  

    def run():
        pass