from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.messages import (
    cancel_button_message,
    deactivate_button_message,
    change_food_courts_button_message
)


class AutomaticReserveAlreadyActivatedHandler:
    @staticmethod
    def create_keyboard() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([[
            InlineKeyboardButton(
                change_food_courts_button_message, callback_data=AutomaticReserveAlreadyActivatedHandler.create_callback_data("CHANGE_FOOD_COURTS")),
            InlineKeyboardButton(
                cancel_button_message, callback_data=AutomaticReserveAlreadyActivatedHandler.create_callback_data("CANCEL")),
            InlineKeyboardButton(
                deactivate_button_message, callback_data=AutomaticReserveAlreadyActivatedHandler.create_callback_data("DEACTIVATE"))
        ]])

    @staticmethod
    def create_callback_data(action: str) -> str:
        return "AUTOMATIC_RESERVE" + ";" + ";".join([action])

    @staticmethod
    def separate_callback_data(data: str) -> list:
        return data.split(";")