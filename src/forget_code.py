from telegram import ReplyKeyboardMarkup
import src.messages as messages
import src.static_data as static_data
from src.db import DB


class ForgetCodeMenuHandler:
    FORGET_CODE_LENGTH = 7

    def __init__(self) -> None:
        self.markup = ReplyKeyboardMarkup(static_data.SELFS, one_time_keyboard=True)

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
        # TODO
        # Check is there a forget code for selected self
        choosed_self = update.message.text
        print(choosed_self)
        self.send_forget_code_menu(update, context)
        return static_data.FORGET_CODE_MENU_CHOOSING

    def handle_choosed_self_to_give(self, update, context):
        choosed_self = update.message.text
        context.user_data['self'] = choosed_self
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
        print(forget_code)