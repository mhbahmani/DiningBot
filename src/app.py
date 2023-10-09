import threading
from src.error_handlers import ErrorHandler
from src.inline_keyboards_handlers.automatic_reserve_already_activated_handler import (
    AutomaticReserveAlreadyActivatedHandler)
from src.inline_keyboards_handlers.choose_food_courts_handler import (
    FoodCourtSelectingHandler)
from src.inline_keyboards_handlers.food_priorities_handler import (
    FoodPrioritiesHandler)
from src.db import DB
from src.forget_code import ForgetCodeMenuHandler
from src.reserve import ReserveMenuHandler
from src.static_data import *
from src.utils import update_environment_variable
from telegram import ReplyKeyboardMarkup, Update, error
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ApplicationBuilder,
    filters
)
# from telegram.ext.filters import filters

import src.messages as messages
import logging



class DiningBot:
    def __init__(
        self,
        token, admin_ids=set(),
        sentry_dsn: str = None,
        environment: str = "development",
        log_level='INFO', db: DB = None,
        admin_sso_username: str = None, admin_sso_password: str = None):

        self.admin_ids = admin_ids
        # self.updater = Updater(token=token, use_context=True)
        #self.dispatcher = self.updater.dispatcher

        self.application = ApplicationBuilder().token(token).build()
        self.dispatcher = self.application

        self.db = db

        self.error_handler = ErrorHandler(admin_ids, sentry_dsn, environment)
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
        async def wrapper(self, *args, **kwargs):
            update, _ = args[0], args[1]
            user_id = update.message.chat.id
            if user_id not in self.admin_ids:
                msg = messages.you_are_not_admin_message
                logging.info(f"{update.effective_user.username} is trying to run an admin command")
                await update.message.reply_text(text=msg)
                return
            return await func(self, *args, **kwargs)
        return wrapper

    def is_admin(self, update):
        return update.message.chat.id in self.admin_ids

    async def send_msg_to_admins(self, context, message):
        for admin_id in self.admin_ids:
            await context.bot.send_message(
                admin_id, message
            )

    async def start(self, update, context):
        if self.db.add_bot_user({
            "user_id": update.effective_user.id,
            "username": update.effective_user.username,
            "forget_code": None}):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=messages.start_message)
            await self.send_msg_to_admins(
                context,
                messages.new_user_message.format(update.effective_user.username))
        await self.send_main_menu(update, context)
        return MAIN_MENU_CHOOSING

    @check_admin
    async def set(self, update, context):
        if not update.message.text: return # on edit
        args = update.message.text.split()[1:]
        if len(args) != 2:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=messages.set_wrong_args_message)
            return
        student_number, password = args
        update_environment_variable("ADMIN_SHARIF_SSO_USERNAME", student_number)
        update_environment_variable("ADMIN_SHARIF_SSO_PASSWORD", password)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=messages.set_result_message.format(student_number, password))

    @check_admin
    async def automatic_reserve_food(self, update, context):
        if not update.message.text: return
        splited_text = update.message.text.split()
        username = None
        if len(splited_text) == 2:
            username = splited_text[-1]
        elif len(splited_text) < 2:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=messages.no_username_specified_error_message)
            return
        try:
            user_id = self.db.get_user_id_by_username(username)
        except AttributeError as e:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=messages.automatic_reserve_no_such_username_message)
            return
        await self.reserve_handler.automatic_reserve(context, user_id, update.effective_chat.id)

    async def help(self, update, context):
        if self.is_admin(update):
            msg = messages.admin_help_message
        else:
            msg = messages.help_message
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg)

    async def inline_keyboard_handler(self, update, context):
        type = FoodPrioritiesHandler.separate_callback_data(update.callback_query.data)[0]
        if type == "FOOD":
            _, action, choosed, page = FoodPrioritiesHandler.separate_callback_data(update.callback_query.data)
            return await self.reserve_handler.inline_food_choosing_handler(update, context, action, choosed, int(page))
        elif type == "FOODCOURT":
            _, action, choosed = FoodCourtSelectingHandler.separate_callback_data(update.callback_query.data)
            return await self.reserve_handler.inline_food_court_choosing_handler(update, context, action, choosed)
        elif type == "FORGETCODE":
            _, forget_code = ForgetCodeMenuHandler.separate_callback_data(update.callback_query.data)
            await self.forget_code_handler.inline_return_forget_code_handler(update, context, int(forget_code))
        elif type == "AUTOMATIC_RESERVE":
            _, action = AutomaticReserveAlreadyActivatedHandler.separate_callback_data(update.callback_query.data)
            await self.reserve_handler.inline_already_activated_handler(update, context, action)

    async def send_main_menu(self, update, context):
        if context.user_data: context.user_data.clear()
        await update.message.reply_text(
            text=messages.main_menu_message,
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_CHOICES),
        )
        return MAIN_MENU_CHOOSING

    async def unknown_command(self, update, context):
        await update.message.reply_text(
            text=messages.restart_bot_message,
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_CHOICES),
        )
        return MAIN_MENU_CHOOSING

    @check_admin
    async def send_to_all(self, update, context):
        import re
        msg = re.sub("/sendmsgtoall", "", update.message.text)
        # threading.Thread(target=self.send_message_to_all_handler, args=(context, msg,)).start()
        await self.send_message_to_all_handler(context, msg)

    async def send_message_to_all_handler(self, context, msg):
        users = self.db.get_all_bot_users()
        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user["user_id"],
                    text=msg
                )
            except error.Unauthorized:
                continue
        await self.send_msg_to_admins(context, messages.send_to_all_done_message)

    @check_admin
    async def update_foods_list_database(self, update, context):
        await update.message.reply_text(
            text=messages.update_foods_started_message
        )
        # /update_foods <week>
        splited_text = update.message.text.split()
        week = 0
        if len(splited_text) == 2:
            week = splited_text[-1]
        await self.reserve_handler.update_food_list(update, context, int(week))

    def setup_handlers(self):        
        help_handler = CommandHandler('help', self.help, block=False)
        self.dispatcher.add_handler(help_handler)

        set_handler = CommandHandler('set', self.set, block=False)
        self.dispatcher.add_handler(set_handler)

        sendtoall_handler = CommandHandler('sendmsgtoall', self.send_to_all, block=False)
        self.dispatcher.add_handler(sendtoall_handler)

        update_food_list_handler = CommandHandler('update_foods', self.update_foods_list_database, block=False)
        self.dispatcher.add_handler(update_food_list_handler)

        reserve_food_handler = CommandHandler('reserve', self.automatic_reserve_food, block=False)
        self.dispatcher.add_handler(reserve_food_handler)

        inline_handler = CallbackQueryHandler(self.inline_keyboard_handler, block=False)
        self.dispatcher.add_handler(inline_handler)

        menue_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start), MessageHandler(filters.TEXT & (~filters.COMMAND), self.unknown_command)],
            states={
                MAIN_MENU_CHOOSING: [
                    MessageHandler(
                        filters.Regex(FORGET_CODE_MENU_REGEX),
                        self.forget_code_handler.send_forget_code_menu,
                        block=False
                    ),
                    MessageHandler(
                        filters.Regex(RESERVE_MENU_REGEX),
                        self.reserve_handler.send_reserve_menu,
                        block=False
                    )
                ],
                RESERVE_MENU_CHOOSING: [
                    MessageHandler(
                        filters.Regex(SET_FAVORITES_REGEX),
                        self.reserve_handler.update_user_favorite_foods,
                        block=False
                    ),
                    MessageHandler(
                        filters.Regex(SHOW_FAVORITES_REGEX),
                        self.reserve_handler.show_favorite_foods,
                        block=False
                    ),
                    MessageHandler(
                        filters.Regex(RESERVE_REGEX),
                        self.reserve_handler.reserve_next_week_food
                    ),
                    MessageHandler(
                        filters.Regex(SET_USERNAME_AND_PASSWORD_REGEX),
                        self.reserve_handler.set_username_and_password_handler,
                        block=False
                    ),
                    MessageHandler(
                        filters.Regex(ACTIVATE_AUTOMATIC_RESERVE_REGEX),
                        self.reserve_handler.activate_automatic_reserve_handler,
                        block=False
                    )
                ],
                INPUT_USERNAME: [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND | filters.Regex(INPUT_USERNAME_AND_PASSWORD_EXCLUDE)),
                        self.reserve_handler.handle_username_input,
                        block=False
                    )
                ],
                INPUT_PASSWORD: [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND | filters.Regex(INPUT_USERNAME_AND_PASSWORD_EXCLUDE)),
                        self.reserve_handler.handle_password_input,
                        block=False
                    )
                ],
                FORGET_CODE_MENU_CHOOSING: [
                    MessageHandler(
                        filters.Regex(GET_FORGET_CODE_REGEX),
                        self.forget_code_handler.send_choose_food_court_menu_to_get,
                        block=False
                    ),
                    MessageHandler(
                        filters.Regex(GIVE_FORGET_CODE_REGEX),
                        self.forget_code_handler.send_choose_food_court_menu_to_give,
                        block=False
                    ),
                    MessageHandler(
                        filters.Regex(RANKING_FORGET_CODE_REGEX),
                        self.forget_code_handler.send_forget_code_ranking,
                        block=False
                    ),
                    MessageHandler(
                        filters.Regex(FAKE_FORGET_CODE_REGEX),
                        self.forget_code_handler.get_fake_forget_code,
                        block=False
                    ),
                    MessageHandler(
                        filters.Regex(TODAY_CODE_STATISTICS_REGEX),
                        self.forget_code_handler.forget_code_statistics,
                        block=False
                    )
                ],
                CHOOSING_SELF_TO_GET: [
                    MessageHandler(
                        filters.Regex(FOOD_COURTS_REGEX),
                        self.forget_code_handler.handle_choosed_food_court_to_get
                    )
                ],
                CHOOSING_SELF_TO_GIVE: [
                    MessageHandler(
                        filters.Regex(FOOD_COURTS_REGEX),
                        self.forget_code_handler.handle_choosed_food_court_to_give,
                        block=False
                    )
                ],
                INPUT_FOOD_NAME: [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND | filters.Regex(INPUT_FORGET_CODE_EXCLUDE)),
                        self.forget_code_handler.handle_forget_code_food_name_input,
                        block=False
                    )
                ],
                INPUT_FORGET_CODE: [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND | filters.Regex(INPUT_FORGET_CODE_EXCLUDE)),
                        self.forget_code_handler.handle_forget_code_input,
                        block=False
                    )
                ],
                INPUT_FAKE_FORGET_CODE: [
                    MessageHandler(
                        filters.TEXT & ~(filters.COMMAND | filters.Regex(INPUT_FORGET_CODE_EXCLUDE)),
                        self.forget_code_handler.handle_fake_forget_code_input,
                        block=False
                    )
                ],
            },
            fallbacks=[MessageHandler(filters.Regex(BACK_TO_MAIN_MENU_REGEX), self.send_main_menu)],
        )
        self.dispatcher.add_handler(menue_handler)

        self.dispatcher.add_error_handler(self.error_handler.handle_error)


    def run(self):
        self.reserve_handler.load_foods()
        self.setup_handlers()
        #self.updater.start_polling()
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

        # self.updater.idle()
