from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.static_data import WEEK_DAYS, UNIVERSITY_FOOD_COURT_IDS
from src.messages import (
    done_button_message,
    cancel_button_message
)


PAGE_SIZE = 10

class ChooseReserveDaysHandler:
    @staticmethod
    def create_days_list_keyboard(food_court) -> InlineKeyboardMarkup:
        keyboard = []
        day_number = 0
        max_day_number = 5 if food_court in UNIVERSITY_FOOD_COURT_IDS else 6
        
        while day_number < max_day_number:
            row = []
            for _ in range(2):
                if day_number >= max_day_number:
                    break
                row.insert(
                    0,
                    InlineKeyboardButton(
                        WEEK_DAYS[day_number],
                        callback_data=ChooseReserveDaysHandler.create_callback_data(
                            action="SELECT", food_court=str(food_court), day_id=str(day_number))))
                day_number += 1
            keyboard.append(row)

        row = []
        row.append(
            InlineKeyboardButton(
                cancel_button_message, callback_data=ChooseReserveDaysHandler.create_callback_data("CANCEL")))
        row.append(
            InlineKeyboardButton(
                done_button_message, callback_data=ChooseReserveDaysHandler.create_callback_data("DONE")))
        keyboard.append(row)

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def create_callback_data(action: str, food_court: str = "-", day_id: str = "-") -> str:
        return "DAYS/DAYS" + ";" + ";".join([action, str(food_court), str(day_id)])

    @staticmethod
    def separate_callback_data(data: str) -> list:
        return data.split(";")