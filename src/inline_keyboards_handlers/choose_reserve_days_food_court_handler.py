from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.messages import (
    next_page_button_message,
    previous_page_button_message,
    done_button_message,
    cancel_button_message
)


PAGE_SIZE = 10

class ChooseReserveDaysHandler:
    @staticmethod
    def create_food_list_keyboard(food_courts: dict) -> InlineKeyboardMarkup:
        keyboard = []
        food_courts = list(food_courts.items())
        food_courts.reverse()

        while food_courts:
            row = []
            for _ in range(3):
                if not food_courts: break
                food_court_name, food_court_id = food_courts.pop()
                row.append(
                    InlineKeyboardButton(
                        food_court_name,
                        callback_data=ChooseReserveDaysHandler.create_callback_data(
                            action="SELECT", food_court_id=food_court_id)))
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
    def create_callback_data(action: str, food_court_id: str = "-") -> str:
        return "DAYS/FOOD_COURTS" + ";" + ";".join([action, food_court_id])

    @staticmethod
    def separate_callback_data(data: str) -> list:
        return data.split(";")