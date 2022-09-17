from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.messages import (
    cancel_button_message,
    done_button_message
)
from src.static_data import WEEK_DAYS

class WeekDaysHandler:
    @staticmethod
    def create_week_days_keyboard() -> InlineKeyboardMarkup:
        keyboard = []
        for day in WEEK_DAYS:
            keyboard.append([
                InlineKeyboardButton(
                    day, callback_data=WeekDaysHandler.create_callback_data(action="SELECT", day=WEEK_DAYS[day]))
            ])

        keyboard.append([
            InlineKeyboardButton(
                cancel_button_message, callback_data=WeekDaysHandler.create_callback_data(action="CANCEL")),
            InlineKeyboardButton(
                done_button_message, callback_data=WeekDaysHandler.create_callback_data(action="DONE"))
        ])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def create_callback_data(action: str, day="-") -> str:
        return "FOODCOURTDAYSCHOOSING" + ";" + ";".join([action, str(day)])

    @staticmethod
    def separate_callback_data(data: str) -> list:
        return data.split(";")