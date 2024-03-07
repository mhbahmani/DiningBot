from random import randint
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from src.utils import get_food_court_id_by_name, make_forget_code_statistics_message
from src.rest_dining import Samad 
import src.messages as messages
import src.static_data as static_data

class ForgetCodeMenuHandler:
    FORGET_CODE_MINIMUM_LENGTH = 6
    FORGET_CODE_MAXIMUM_LENGTH = 7

    def __init__(self, db_client) -> None:
        self.db = db_client
        self.markup = ReplyKeyboardMarkup(static_data.SELFS)

        self.today_forget_codes = set()

    async def send_forget_code_menu(self, update, context):
        await update.message.reply_text(
            text=messages.forget_code_menu_message,
            reply_markup=ReplyKeyboardMarkup(static_data.FORGET_CODE_MENU_CHOICES),
        )
        return static_data.FORGET_CODE_MENU_CHOOSING

    async def send_choose_food_court_menu_to_get(self, update, context):
        if self.db.get_user_current_forget_code(update.effective_user.id):
            await update.message.reply_text(
                text=messages.you_already_have_forget_code_message,
            )
            return static_data.FORGET_CODE_MENU_CHOOSING
        await update.message.reply_text(
            text=messages.choose_food_court_message_to_get,
            reply_markup=self.markup,
        )
        return static_data.CHOOSING_SELF_TO_GET

    async def send_choose_food_court_menu_to_give(self, update, context):
        await update.message.reply_text(
            text=messages.choose_food_court_message_to_give,
            reply_markup=self.markup,
        )
        return static_data.CHOOSING_SELF_TO_GIVE

    async def handle_choosed_food_court_to_get(self, update, context):
        choosed_food_court = update.message.text
        forget_codes = list(self.db.find_forget_code(get_food_court_id_by_name(choosed_food_court)))
        if not forget_codes:
            await update.message.reply_text(
                text=messages.no_code_for_this_food_court_message
            )
            return await self.send_choose_food_court_menu_to_get(update, context)
        # Assign a random code to user
        forget_code = forget_codes[randint(0, len(forget_codes) - 1)]
        await update.message.reply_text(
            text=messages.forget_code_founded_message.format(forget_code.get("forget_code"), choosed_food_court, forget_code.get("food_name"), forget_code.get("username")),
            reply_markup=self.make_return_forget_code_button(forget_code.get("forget_code"))
        )
        # If forget code is in today_forget_codes, it means bot should notify the code owner
        if forget_code.get("forget_code") in self.today_forget_codes:    
            await context.bot.send_message(
                chat_id=forget_code.get("user_id"),
                text=messages.someone_took_your_code_message
            )
            self.today_forget_codes.remove(forget_code.get("forget_code"))
        self.db.set_forget_code_for_user(update.effective_user.id, forget_code.get("forget_code"))
        self.db.update_forget_code_assignment_status(int(forget_code.get("forget_code")), True, update.effective_user.id, update.effective_user.username)
        await self.back_to_main_menu(update)
        return static_data.MAIN_MENU_CHOOSING

    async def handle_choosed_food_court_to_give(self, update, context):
        choosed_food_court = update.message.text
        context.user_data['food_court'] = choosed_food_court
        await update.message.reply_text(
            text=messages.get_forget_code_from_user_message,
            reply_markup=ReplyKeyboardMarkup(static_data.BACK_TO_MAIN_MENU_CHOICES)
        )
        return static_data.INPUT_FORGET_CODE

    async def handle_forget_code_input(self, update, context):
        forget_code = update.message.text
        try:
            forget_code = int(forget_code)
        except ValueError:
            await update.message.reply_text(
                text=messages.not_int_code_error_message
            )
            return static_data.INPUT_FORGET_CODE
        if not context.user_data['food_court']:
            await update.message.reply_text(
                text=messages.food_court_not_choosed_error_message
            )
            return static_data.CHOOSING_SELF_TO_GIVE
        context.user_data['forget_code'] = forget_code
        await update.message.reply_text(
            text=messages.get_food_name_message
        )
        return static_data.INPUT_FOOD_NAME
    
    async def handle_forget_code_food_name_input(self, update, context):
        # TODO: Handle duplicate forget code
        res = self.db.add_forget_code({
            "username": update.effective_user.username,
            "user_id": update.message.chat.id,
            "forget_code": context.user_data['forget_code'],
            "food_name": update.message.text,
            "food_court_id": get_food_court_id_by_name(context.user_data['food_court']),
            "assigned": False,
            "assigned_to_user_id": None,
            "asssigned_to_username": None,
            "counted": False
        })
        if not res:
            await update.message.reply_text(
                text=messages.duplicate_forget_code_message
            )
            return static_data.MAIN_MENU_CHOOSING
        await update.message.reply_text(
            text=messages.forget_code_added_message
        )
        # TODO: Change this to a more elegant way
        # Adding forget code to today_forget_codes to notify the user if someone took it
        self.today_forget_codes.add(context.user_data['forget_code'])
        if context.user_data: context.user_data.clear()
        await self.back_to_main_menu(update)
        return static_data.MAIN_MENU_CHOOSING

    async def send_forget_code_ranking(self, update, context):
        users = list(self.db.get_users_forget_code_counts())
        if users:
            users = users[:50]
        else:
            await update.message.reply_text(
                text=messages.no_one_added_code_yet_message
            )
            return static_data.FORGET_CODE_MENU_CHOOSING
        message = ""
        for i, user in enumerate(users):
            message += messages.ranking_message.format(i + 1, user.get("username"), user.get("count"))
        message += messages.user_rank_message.format(
            self.db.get_user_rank(update.effective_user.id).get('rank', messages.rank_not_found_message),
            self.db.get_num_users())
        await update.message.reply_text(
            text=messages.users_ranking_message.format(message)
        )
        return static_data.FORGET_CODE_MENU_CHOOSING

    async def back_to_main_menu(self, update):
        await update.message.reply_text(
            text=messages.main_menu_message,
            reply_markup=ReplyKeyboardMarkup(static_data.MAIN_MENU_CHOICES),
        )
    
    async def inline_return_forget_code_handler(self, update, context, forget_code: int):
        self.db.update_forget_code_assignment_status(forget_code)
        await context.bot.edit_message_text(
            text=messages.forget_taked_back_message,
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id
        )
        self.db.set_forget_code_for_user(update.effective_user.id, None)

    async def get_user_forget_codes_for_today_reserves(self, update, context):
        user_info = self.db.get_user_info_by_id(update.effective_user.id)
        if not user_info or not user_info.get("student_number") or not user_info.get("password"):
            await update.message.reply_text(
                text=messages.username_and_password_not_set_message,
            )
            await self.back_to_main_menu(update)
            return static_data.MAIN_MENU_CHOOSING
        
        dining = Samad(user_info.get("student_number"), user_info.get("password"))
        today_reserve_forget_codes = dining.get_current_day_all_forget_codes()
        if not today_reserve_forget_codes:
            await update.message.reply_text(
                text=messages.no_food_reserved_today_message,
            )
        else:
            for forget_code in today_reserve_forget_codes:        
                await update.message.reply_text(
                    text=self.forget_code_list_message(forget_code),
                )
        return await self.send_forget_code_menu(update, context)

    async def get_fake_forget_code(self, update, context):
        await update.message.reply_text(
            text=messages.fake_forget_code_report_message,
            reply_markup=ReplyKeyboardMarkup(static_data.BACK_TO_MAIN_MENU_CHOICES),
        )
        return static_data.INPUT_FAKE_FORGET_CODE

    async def forget_code_statistics(self, update, context):
        await update.message.reply_text(
            text=make_forget_code_statistics_message(self.db.get_forget_codes_by_food_court_id()))
        return static_data.FORGET_CODE_MENU_CHOOSING

    async def handle_fake_forget_code_input(self, update, context):
        fake_forget_code = update.message.text
        if len(fake_forget_code) < ForgetCodeMenuHandler.FORGET_CODE_MINIMUM_LENGTH \
            or len(fake_forget_code) > ForgetCodeMenuHandler.FORGET_CODE_MAXIMUM_LENGTH:
            await update.message.reply_text(
                text=messages.not_enough_number_error_message
            )
            return static_data.INPUT_FAKE_FORGET_CODE
        try:
            fake_forget_code = int(fake_forget_code)
        except ValueError:
            await update.message.reply_text(
                text=messages.not_int_code_error_message
            )
            return static_data.INPUT_FAKE_FORGET_CODE
        forget_code = self.db.get_forget_code_info(fake_forget_code)
        # TODO: handle fake forget code some how :)
        self.db.set_forget_code_for_user(update.effective_user.id, forget_code)
        await update.message.reply_text(
            text=messages.fake_forget_code_taked_message,
        )
        await self.back_to_main_menu(update)
        return static_data.MAIN_MENU_CHOOSING
    
    def forget_code_list_message(self, forget_code: dict) -> str:
        return messages.forget_code_list_message.format(
            static_data.MEAL_EN_TO_FA.get(static_data.MEALS_ID_TO_NAME.get(str(forget_code.get("meal_type_id"))), messages.unkonw_meal_type),
            forget_code.get("food_court_name"),
            forget_code.get("food_name"),
            forget_code.get("forget_code")
        )

    def make_return_forget_code_button(self, forget_code):
        return InlineKeyboardMarkup([[InlineKeyboardButton(
                    messages.i_dont_want_this_code_message,
                    callback_data=ForgetCodeMenuHandler.create_callback_data(forget_code))]])

    @staticmethod
    def create_callback_data(forget_code) -> str:
        return "FORGETCODE" + ";" + ";".join([str(forget_code)])

    @staticmethod
    def separate_callback_data(data: str) -> list:
        return data.split(";")