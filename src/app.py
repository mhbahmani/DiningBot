from threading import Thread
import threading
from src.dining import Dining
from src.db import DB
from src.food_priorities_handler import FoodPrioritiesHandler
from src.forget_code import ForgetCodeMenuHandler
from src.reserve import ReserveMenuHandler
from src.static_data import (
    BACK_TO_MAIN_MENU_LABEL,
    BACK_TO_MAIN_MENU_REGEX,
    FOOD_COURTS_REGEX,
    FORGET_CODE_MENU_REGEX,
    GET_FORGET_CODE_REGEX,
    GIVE_FORGET_CODE_REGEX,
    INPUT_FOOD_NAME,
    INPUT_FORGET_CODE_EXCLUDE,
    PLACES,
    INPUT_FORGET_CODE,
    MAIN_MENU_CHOICES,
    MAIN_MENU_CHOOSING,
    CHOOSING_SELF_TO_GET,
    CHOOSING_SELF_TO_GIVE,
    RANKING_FORGET_CODE_REGEX,
    RESERVE_MENU_CHOOSING,
    FORGET_CODE_MENU_CHOOSING,
    RESERVE_MENU_REGEX,
)
from telegram import (
    ReplyKeyboardMarkup
)
from telegram.ext import (
    Updater,
    Filters,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler
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
        self.foods_with_id = []
        self.food_name_by_id = {}

        self.db = db

        self.forget_code_handler = ForgetCodeMenuHandler(self.db)
        self.reserve_handler = ReserveMenuHandler()
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
        self.send_main_menu(update, context)
        self.send_msg_to_admins(
            context,
            messages.new_user_message.format(update.effective_user.username))
        return MAIN_MENU_CHOOSING

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
        context.user_data['priorities'] = []
        update.message.reply_text(
            text=messages.choose_food_priorities_message,
            reply_markup=FoodPrioritiesHandler.create_food_list_keyboard(
                foods=self.foods_with_id, page=1)
        )

    def inline_keyboard_handler(self, update, context):
        type = FoodPrioritiesHandler.separate_callback_data(update.callback_query.data)[0]
        if type == "FOOD":
            _, action, choosed, page = FoodPrioritiesHandler.separate_callback_data(update.callback_query.data)
            self.inline_food_choosing_handler(update, context, action, choosed, int(page))
        elif type == "FORGETCODE":
            _, forget_code = ForgetCodeMenuHandler.separate_callback_data(update.callback_query.data)
            self.inline_return_forget_code_handler(update, context, int(forget_code))

    def inline_return_forget_code_handler(self, update, context, forget_code: int):
        self.forget_code_handler.return_forget_code(update, context, forget_code)

    def inline_food_choosing_handler(self, update, context, action, choosed, page: int):
        query = update.callback_query
        logging.debug("Process choosed action or food: {} {}".format(action, choosed))
        if action == "NEXT":
            context.bot.edit_message_text(
                text=query.message.text,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                reply_markup=FoodPrioritiesHandler.create_food_list_keyboard(foods=self.foods_with_id, page=page + 1))
        elif action == "PREV":
            context.bot.edit_message_text(
                text=query.message.text,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                reply_markup=FoodPrioritiesHandler.create_food_list_keyboard(foods=self.foods_with_id, page=page - 1))
        elif action == "SELECT":
            context.user_data.get('priorities').append(choosed)
            context.bot.send_message(
                text=self.food_name_by_id[choosed],
                chat_id=update.effective_chat.id
            )
        elif action == "DONE":
            self.db.set_user_food_priorities(update.effective_chat.id, context.user_data.get('priorities'))
            context.user_data['priorities'].clear()
            context.bot.edit_message_text(
                text=messages.choosing_food_priorities_done_message,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)
        elif action == "CANCEL":
            context.user_data['priorities'].clear()
            context.bot.edit_message_text(
                text=messages.choosing_food_priorities_cancel_message,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)     
        elif action == "IGNORE":
            context.bot.answer_callback_query(callback_query_id=query.id)
            
    def load_foods(self):
        for food in self.db.get_all_foods(name=True, id=True):
            self.foods.add(food['name'])
            self.foods_with_id.append((food['id'], food['name']))
            self.food_name_by_id[food['id']] = food['name']
        logging.info(f"Loaded {len(self.foods)} foods")

    def update_food_lists_caches(self):
        for food in self.db.get_all_foods(name=True, id=True):
            self.foods_with_id.append((food['id'], food['name']))
            self.food_name_by_id[food['id']] = food['name']

    @check_admin
    def update_food_list(self, update, context):
        self.dining = Dining(self.admin_username, self.admin_password)
        new_foods = []
        food_id = num_foods = len(self.foods)
        for place_id in PLACES.values():
            table = self.dining.get_foods_list(place_id)
            new_foods = list(set(table) - self.foods)
            for food_name in new_foods:
                food_id += 1
                self.db.add_food({"name": food_name, "id": str(food_id)})
                logging.debug("Added food: {} {}".format(food_name, food_id))
            self.foods.update(table)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=messages.update_food_list_result.format(len(self.foods) - num_foods))
        logging.info(f"{len(self.foods) - num_foods} foods added")
        threading.Thread(target=self.update_food_lists_caches, args=()).start()
        logging.info("Updated food list in cache started")

    def send_main_menu(self, update, context):
        update.message.reply_text(
            text=messages.main_menu_message,
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_CHOICES),
        )
        return MAIN_MENU_CHOOSING

    def setup_handlers(self):
        help_handler = CommandHandler('help', self.help)
        self.dispatcher.add_handler(help_handler)

        set_handler = CommandHandler('set', self.set)
        self.dispatcher.add_handler(set_handler)

        update_food_list_handler = CommandHandler('update_foods', self.update_food_list)
        self.dispatcher.add_handler(update_food_list_handler)

        my_foods_handler = CommandHandler('my_foods', self.update_user_favorite_foods)
        self.dispatcher.add_handler(my_foods_handler)

        inline_handler = CallbackQueryHandler(self.inline_keyboard_handler)
        self.dispatcher.add_handler(inline_handler)

        menue_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                MAIN_MENU_CHOOSING: [
                    MessageHandler(
                        Filters.regex(FORGET_CODE_MENU_REGEX),
                        self.forget_code_handler.send_forget_code_menu
                    ),
                    MessageHandler(
                        Filters.regex(RESERVE_MENU_REGEX),
                        self.reserve_handler.send_reserve_menu
                    )
                ],
                FORGET_CODE_MENU_CHOOSING: [
                    MessageHandler(
                        Filters.regex(GET_FORGET_CODE_REGEX),
                        self.forget_code_handler.send_choose_self_menu_to_get
                    ),
                    MessageHandler(
                        Filters.regex(GIVE_FORGET_CODE_REGEX),
                        self.forget_code_handler.send_choose_self_menu_to_give
                    ),
                    MessageHandler(
                        Filters.regex(RANKING_FORGET_CODE_REGEX),
                        self.forget_code_handler.send_forget_code_ranking
                    )
                ],
                RESERVE_MENU_CHOOSING: [
                    # TODO
                ],
                CHOOSING_SELF_TO_GET: [
                    MessageHandler(
                        Filters.regex(FOOD_COURTS_REGEX),
                        self.forget_code_handler.handle_choosed_self_to_get
                    )
                ],
                CHOOSING_SELF_TO_GIVE: [
                    MessageHandler(
                        Filters.regex(FOOD_COURTS_REGEX),
                        self.forget_code_handler.handle_choosed_self_to_give
                    )
                ],
                INPUT_FOOD_NAME: [
                    MessageHandler(
                        Filters.text & ~(Filters.command | Filters.regex(INPUT_FORGET_CODE_EXCLUDE)),
                        self.forget_code_handler.handle_forget_code_food_name_input
                    )                    
                ],
                INPUT_FORGET_CODE: [
                    MessageHandler(
                        Filters.text & ~(Filters.command | Filters.regex(INPUT_FORGET_CODE_EXCLUDE)),
                        self.forget_code_handler.handle_forget_code_input
                    )                    
                ],
            },
            fallbacks=[MessageHandler(Filters.regex(BACK_TO_MAIN_MENU_REGEX), self.send_main_menu)],
        )
        self.dispatcher.add_handler(menue_handler)

    def run(self):
        self.load_foods()
        self.setup_handlers()
        self.updater.start_polling()

        self.updater.idle()
