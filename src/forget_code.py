from telegram import ReplyKeyboardMarkup
import src.messages as messages
import src.static_data as static_data
from src.db import DB


class ForgetCodeMenuHandler:
    def __init__(self) -> None:
        self.markup = ReplyKeyboardMarkup(static_data.SELFS, one_time_keyboard=True)

    def send_forget_code_menu(self, update, context):
        update.message.reply_text(
            text=messages.forget_code_menu_message,
            reply_markup=ReplyKeyboardMarkup(static_data.FORGET_CODE_MENU_CHOICES, one_time_keyboard=True),
        )
        return static_data.FORGET_CODE_MENU_CHOOSING

    def send_choose_self_menu(self, update, context):
        update.message.reply_text(
            text=messages.choose_self_message,
            reply_markup=self.markup,
        )
        return static_data.CHOOSING_SELF

    def handle_choosing_self(self, update, context):
        # TODO
        # Check is there a forget code for selected self
        choosed_self = update.message.text
        print(choosed_self)
        self.send_forget_code_menu(update, context)
        return static_data.FORGET_CODE_MENU_CHOOSING