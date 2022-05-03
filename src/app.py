from src.dining import Dining
from src.db import DB
from src.food_priorities_handler import FoodPrioritiesHandler
from src.static_data import (
    PLACES
)
from telegram.ext import (
    Updater,
    CommandHandler,
)

import src.messages as messages
import logging


class DiningBot:
    def __init__(self, token, admin_ids=set(), log_level='INFO', db: DB = None, admin_sso_username: str = None, admin_sso_password: str = None):
        self.admin_ids = admin_ids
        self.admin_username = admin_sso_username
        self.admin_password = admin_sso_password
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.foods = set()

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
        logging.info("Add user: {} {} to db".format(student_number, password))
        self.db.add_user({
            "user_id": update.message.chat.id,
            "username": update.effective_user.username,
            "student_number": student_number,
            "password": password})
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

    def update_user_favorite_foods(self, update, context):
        update.message.reply_text(
            text=messages.choose_food_priorities_message,
            reply_markup=FoodPrioritiesHandler.create_food_list_keyboard(foods=self.foods, page=1)
        )

    def load_foods(self):
        foods = [food.get("name") for food in self.db.get_all_foods()]
        self.foods = set(foods)
        logging.info(f"Loaded {len(self.foods)} foods")

    @check_admin
    def update_food_list(self, update, context):
        self.dining = Dining(self.admin_username, self.admin_password)
        num_foods = len(self.foods)
        new_foods = []
        for place_id in PLACES.values():
            table = self.dining.get_foods_list(place_id)
            new_foods = list(set(table) - self.foods)
            for new_food in new_foods:
                self.db.add_food({"name": new_food})
                logging.debug("Added food: {}".format(new_food))
            self.foods.update(table)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=messages.update_food_list_result.format(len(self.foods) - num_foods))

    def setup_handlers(self):
        start_handler = CommandHandler('start', self.start)
        self.dispatcher.add_handler(start_handler)

        help_handler = CommandHandler('help', self.help)
        self.dispatcher.add_handler(help_handler)

        set_handler = CommandHandler('set', self.set)
        self.dispatcher.add_handler(set_handler)

        update_food_list_handler = CommandHandler('update_foods', self.update_food_list)
        self.dispatcher.add_handler(update_food_list_handler)

        my_foods_handler = CommandHandler('my_foods', self.update_user_favorite_foods)
        self.dispatcher.add_handler(my_foods_handler)


    def run(self):
        self.load_foods()
        self.setup_handlers()
        self.updater.start_polling()

        self.updater.idle()
