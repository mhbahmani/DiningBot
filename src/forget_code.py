from telegram import ReplyKeyboardMarkup
import src.messages as messages
import src.static_data as static_data


class ForgetCodeMenuHandler:
    def __init__(self) -> None:
        pass

    def send_forget_code_menu(self, update, context):
        update.message.reply_text(
            text=messages.forget_code_menu_message,
            reply_markup=ReplyKeyboardMarkup(static_data.FORGET_CODE_MENU_CHOICES, one_time_keyboard=True),
        )
        return static_data.FORGET_CODE_MENU_CHOOSING

    def send_choose_self_menu(self, update, context):
        update.message.reply_text(
            text=messages.choose_self_message,
            reply_markup=ReplyKeyboardMarkup(static_data.SELFS, one_time_keyboard=True),
        )
        return static_data.CHOOSING_SELF