from telegram import ReplyKeyboardMarkup
import src.messages as messages
import src.static_data as static_data


class ReserveMenuHandler:
    def __init__(self) -> None:
        pass

    def send_reserve_menu(self, update, context):
        # update.message.reply_text(
        #     text=messages.still_under_struction,
        # )
        # return static_data.MAIN_MENU_CHOOSING
        update.message.reply_text(
            text=messages.reserve_menu_messsage,
            reply_markup=ReplyKeyboardMarkup(static_data.RESERVE_MENU_CHOICES),
        )
        return static_data.RESERVE_MENU_CHOOSING

    def update_favorties(self, update, context):
        update.message.reply_text(
            text=messages.still_under_struction,
        )
        return static_data.RESERVE_MENU_CHOOSING

    def reserve_next_week_food(self, update, context):
        update.message.reply_text(
            text=messages.still_under_struction,
        )
        return static_data.RESERVE_MENU_CHOOSING