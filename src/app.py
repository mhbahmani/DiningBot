from src.automatic_reserve_already_activated_handler import AutomaticReserveAlreadyActivatedHandler
from src.choose_food_courts_handler import FoodCourtSelectingHandler
from src.db import DB
from src.food_priorities_handler import FoodPrioritiesHandler
from src.forget_code import ForgetCodeMenuHandler
from src.reserve import ReserveMenuHandler
from src.static_data import *
from src.utils import update_environment_variable
from telegram import ReplyKeyboardMarkup, error
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
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.db = db

        self.forget_code_handler = ForgetCodeMenuHandler(self.db)
        self.reserve_handler = ReserveMenuHandler(self.db, admin_sso_username, admin_sso_password)

        logging.basicConfig(
            format='%(asctime)s - %(levelname)s - %(message)s',
            level={
                'INFO': logging.INFO,
                'DEBUG': logging.DEBUG,
                'ERROR': logging.ERROR,
            }[log_level])

    def check_admin(func):
        def wrapper(self, *args, **kwargs):
            update, _ = args[0], args[1]
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
        if self.db.add_bot_user({
            "user_id": update.effective_user.id,
            "username": update.effective_user.username,
            "forget_code": None}):
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=messages.start_message)
            self.send_msg_to_admins(
                context,
                messages.new_user_message.format(update.effective_user.username))
        self.send_main_menu(update, context)
        return MAIN_MENU_CHOOSING

    @check_admin
    def set(self, update, context):
        if not update.message.text: return # on edit
        args = update.message.text.split()[1:]
        if len(args) != 2:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=messages.set_wrong_args_message)
            return
        student_number, password = args
        update_environment_variable("ADMIN_SHARIF_SSO_USERNAME", student_number)
        update_environment_variable("ADMIN_SHARIF_SSO_PASSWORD", password)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=messages.set_result_message.format(student_number, password))

    @check_admin
    def automatic_reserve_food(self, update, context):
        if not update.message.text: return
        splited_text = update.message.text.split()
        username = None
        if len(splited_text) == 2:
            username = splited_text[-1]
        user_id = self.db.get_user_id_by_username(username)
        self.reserve_handler.automatic_reserve(context, user_id)

    def help(self, update, context):
        if self.is_admin(update):
            msg = messages.admin_help_message
        else:
            msg = messages.help_message
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg)

    def inline_keyboard_handler(self, update, context):
        type = FoodPrioritiesHandler.separate_callback_data(update.callback_query.data)[0]
        if type == "FOOD":
            _, action, choosed, page = FoodPrioritiesHandler.separate_callback_data(update.callback_query.data)
            return self.reserve_handler.inline_food_choosing_handler(update, context, action, choosed, int(page))
        elif type == "FOODCOURT":
            _, action, choosed = FoodCourtSelectingHandler.separate_callback_data(update.callback_query.data)
            return self.reserve_handler.inline_food_court_choosing_handler(update, context, action, choosed)
        elif type == "FORGETCODE":
            _, forget_code = ForgetCodeMenuHandler.separate_callback_data(update.callback_query.data)
            self.forget_code_handler.inline_return_forget_code_handler(update, context, int(forget_code))
        elif type == "AUTOMATIC_RESERVE":
            _, action = AutomaticReserveAlreadyActivatedHandler.separate_callback_data(update.callback_query.data)
            self.reserve_handler.inline_already_activated_handler(update, context, action)

    def send_main_menu(self, update, context):
        if context.user_data: context.user_data.clear()
        update.message.reply_text(
            text=messages.main_menu_message,
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_CHOICES),
        )
        return MAIN_MENU_CHOOSING

    def unknown_command(self, update, context):
        update.message.reply_text(
            text=messages.restart_bot_message,
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_CHOICES),
        )
        return MAIN_MENU_CHOOSING

    @check_admin
    def send_to_all(self, update, context):
        import re
        msg = re.sub("/sendtoall ", "", update.message.text)
        users = self.db.get_all_bot_users()
        for user in users:
            try:
                context.bot.send_message(
                    chat_id=user["user_id"],
                    text=msg
                )
            except error.Unauthorized:
                continue

    @check_admin
    def update_user_favorite_foods(self, update, context):
        update.message.reply_text(
            text=messages.update_foods_started_message
        )
        # /update_foods <week>
        splited_text = update.message.text.split()
        week = 1
        if len(splited_text) == 2:
            week = splited_text[-1]
        self.reserve_handler.update_food_list(update, context, week)

    def setup_handlers(self):
        help_handler = CommandHandler('help', self.help)
        self.dispatcher.add_handler(help_handler)

        set_handler = CommandHandler('set', self.set)
        self.dispatcher.add_handler(set_handler)

        sendtoall_handler = CommandHandler('sendtoall', self.send_to_all)
        self.dispatcher.add_handler(sendtoall_handler)

        update_food_list_handler = CommandHandler('update_foods', self.update_user_favorite_foods)
        self.dispatcher.add_handler(update_food_list_handler)

        reserve_food_handler = CommandHandler('reserve', self.automatic_reserve_food)
        self.dispatcher.add_handler(reserve_food_handler)

        inline_handler = CallbackQueryHandler(self.inline_keyboard_handler)
        self.dispatcher.add_handler(inline_handler)

        menue_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start), MessageHandler(Filters.text & (~Filters.command), self.unknown_command)],
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
                RESERVE_MENU_CHOOSING: [
                    MessageHandler(
                        Filters.regex(SET_FAVORITES_REGEX),
                        self.reserve_handler.update_user_favorite_foods
                    ),
                    MessageHandler(
                        Filters.regex(RESERVE_REGEX),
                        self.reserve_handler.reserve_next_week_food
                    ),
                    MessageHandler(
                        Filters.regex(SET_USERNAME_AND_PASSWORD_REGEX),
                        self.reserve_handler.set_username_and_password_handler
                    ),
                    MessageHandler(
                        Filters.regex(ACTIVATE_AUTOMATIC_RESERVE_REGEX),
                        self.reserve_handler.activate_automatic_reserve_handler
                    )
                ],
                INPUT_USERNAME: [
                    MessageHandler(
                        Filters.text & ~(Filters.command | Filters.regex(INPUT_USERNAME_AND_PASSWORD_EXCLUDE)),
                        self.reserve_handler.handle_username_input
                    )
                ],
                INPUT_PASSWORD: [
                    MessageHandler(
                        Filters.text & ~(Filters.command | Filters.regex(INPUT_USERNAME_AND_PASSWORD_EXCLUDE)),
                        self.reserve_handler.handle_password_input
                    )
                ],
                FORGET_CODE_MENU_CHOOSING: [
                    MessageHandler(
                        Filters.regex(GET_FORGET_CODE_REGEX),
                        self.forget_code_handler.send_choose_food_court_menu_to_get
                    ),
                    MessageHandler(
                        Filters.regex(GIVE_FORGET_CODE_REGEX),
                        self.forget_code_handler.send_choose_food_court_menu_to_give
                    ),
                    MessageHandler(
                        Filters.regex(RANKING_FORGET_CODE_REGEX),
                        self.forget_code_handler.send_forget_code_ranking
                    ),
                    MessageHandler(
                        Filters.regex(FAKE_FORGET_CODE_REGEX),
                        self.forget_code_handler.get_fake_forget_code
                    ),
                    MessageHandler(
                        Filters.regex(TODAY_CODE_STATISTICS_REGEX),
                        self.forget_code_handler.forget_code_statistics
                    )
                ],
                CHOOSING_SELF_TO_GET: [
                    MessageHandler(
                        Filters.regex(FOOD_COURTS_REGEX),
                        self.forget_code_handler.handle_choosed_food_court_to_get
                    )
                ],
                CHOOSING_SELF_TO_GIVE: [
                    MessageHandler(
                        Filters.regex(FOOD_COURTS_REGEX),
                        self.forget_code_handler.handle_choosed_food_court_to_give
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
                INPUT_FAKE_FORGET_CODE: [
                    MessageHandler(
                        Filters.text & ~(Filters.command | Filters.regex(INPUT_FORGET_CODE_EXCLUDE)),
                        self.forget_code_handler.handle_fake_forget_code_input
                    )
                ],
            },
            fallbacks=[MessageHandler(Filters.regex(BACK_TO_MAIN_MENU_REGEX), self.send_main_menu)],
        )
        self.dispatcher.add_handler(menue_handler)


    def run(self):
        self.reserve_handler.load_foods()
        self.setup_handlers()
        self.updater.start_polling()

        self.updater.idle()
