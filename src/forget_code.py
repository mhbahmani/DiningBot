from random import randint
from src.utils import get_food_court_id_by_name
from telegram import ReplyKeyboardMarkup
import src.messages as messages
import src.static_data as static_data


class ForgetCodeMenuHandler:
    FORGET_CODE_LENGTH = 7

    def __init__(self, db_client) -> None:
        self.db = db_client
        self.markup = ReplyKeyboardMarkup(static_data.SELFS)

    def send_forget_code_menu(self, update, context):
        update.message.reply_text(
            text=messages.forget_code_menu_message,
            reply_markup=ReplyKeyboardMarkup(static_data.FORGET_CODE_MENU_CHOICES, one_time_keyboard=True),
        )
        return static_data.FORGET_CODE_MENU_CHOOSING

    def send_choose_self_menu_to_get(self, update, context):
        update.message.reply_text(
            text=messages.choose_self_message_to_get,
            reply_markup=self.markup,
        )
        return static_data.CHOOSING_SELF_TO_GET

    def send_choose_self_menu_to_give(self, update, context):
        update.message.reply_text(
            text=messages.choose_self_message_to_give,
            reply_markup=self.markup,
        )
        return static_data.CHOOSING_SELF_TO_GIVE

    def handle_choosed_self_to_get(self, update, context):
        choosed_food_court = update.message.text
        forget_codes = list(self.db.find_forget_code(get_food_court_id_by_name(choosed_food_court)))
        if not forget_codes:
            update.message.reply_text(
                text=messages.no_code_for_this_food_court_message
            )
            return self.send_choose_self_menu_to_get(update, context)
        forget_code = forget_codes[randint(0, len(forget_codes) - 1)].get("forget_code")
        update.message.reply_text(
            text=messages.forget_code_founded_message.format(forget_code)
        )
        self.back_to_main_menu(update)
        return static_data.MAIN_MENU_CHOOSING

    def handle_choosed_self_to_give(self, update, context):
        choosed_food_court = update.message.text
        context.user_data['food_court'] = choosed_food_court
        update.message.reply_text(
            text=messages.get_forget_code_from_user_message
        )
        return static_data.INPUT_FORGET_CODE

    def handle_forget_code_input(self, update, context):
        forget_code = update.message.text
        if len(forget_code) < ForgetCodeMenuHandler.FORGET_CODE_LENGTH:
            update.message.reply_text(
                text=messages.not_enough_number_error_message
            )
            return static_data.INPUT_FORGET_CODE
        try:
            forget_code = int(forget_code)
        except ValueError:
            update.message.reply_text(
                text=messages.not_int_code_error_message
            )
            return static_data.INPUT_FORGET_CODE
        if not context.user_data['food_court']:
            update.message.reply_text(
                text=messages.food_court_not_choosed_error_message
            )
            return static_data.CHOOSING_SELF_TO_GIVE
        
        self.db.add_forget_code({
            "username": update.effective_user.username,
            "user_id": update.message.chat.id,
            "forget_code": forget_code,
            "food_court_id": get_food_court_id_by_name(context.user_data['food_court'])
        })
        update.message.reply_text(
            text=messages.forget_code_added_message
        )
        if context.user_data: context.user_data.clear()
        self.back_to_main_menu(update)
        return static_data.MAIN_MENU_CHOOSING
    
    def back_to_main_menu(self, update):
        update.message.reply_text(
            text=messages.main_menu_message,
            reply_markup=ReplyKeyboardMarkup(static_data.MAIN_MENU_CHOICES),
        )