from src.dining import Dining
from src.db import DB
from telegram.ext import (
    Updater,
    CommandHandler,
)

import src.messages as messages
import logging


class DiningBot:
    def __init__(self, token, admin_ids=set(), log_level='INFO', db: DB = None):
        self.admin_ids = admin_ids
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.db = db

        # TODO: self.dining = Dining(student_number, password)

        logging.basicConfig(
            format='%(asctime)s - %(levelname)s - %(message)s',
            level={
                'INFO': logging.INFO,
                'DEBUG': logging.DEBUG,
                'ERROR': logging.ERROR,
            }[log_level])

    def check_admin(func):
        def wrapper(self, *args, **kwargs):
            update, context = args[0], args[1]
            user_id = update.message.chat.id
            if user_id not in self.admin_ids:
                msg = messages.you_are_not_admin_message
                update.message.reply_text(text=msg)
                return
            return func(self, *args, **kwargs)
        return wrapper

    def is_admin(self, update):
        return update.message.chat.id in self.admin_ids

    def send_msg_to_admins(self, context, message):
        for admin_id in self.admin_ids:
            context.bot.send_message(
                admin_id, message
            )

    def start(self, update, context):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=messages.start_message)

    def set(self, update, context):
        if not update.message.text: return # on edit
        args = update.message.text.split()[1:]
        if len(args) != 2:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=messages.set_wrong_args_message)
            return
        student_number, password = args
        # TODO
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=messages.set_result_message.format(student_number, password))

    def help(self, update, context):
        if self.is_admin(update):
            msg = messages.admin_help_message
        else:
            msg = messages.help_message
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg)


    def setup_handlers(self):
        start_handler = CommandHandler('start', self.start)
        self.dispatcher.add_handler(start_handler)

        help_handler = CommandHandler('help', self.help)
        self.dispatcher.add_handler(help_handler)

        set_handler = CommandHandler('set', self.set)
        self.dispatcher.add_handler(set_handler)


    def run(self):
        self.setup_handlers()
        self.updater.start_polling()

        self.updater.idle()
