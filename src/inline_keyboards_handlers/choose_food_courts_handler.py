from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.messages import (
    done_button_message,
    cancel_button_message
)


class FoodCourtSelectingHandler:
    @staticmethod
    def create_food_courts_keyboard(food_courts: dict, callback_key: str = "FOODCOURT") -> InlineKeyboardMarkup:
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
                        callback_data=FoodCourtSelectingHandler.create_callback_data(
                            action="SELECT", food_court_id=food_court_id, callback_key=callback_key)))
            keyboard.append(row)

        row = []
        row.append(
            InlineKeyboardButton(
                cancel_button_message, callback_data=FoodCourtSelectingHandler.create_callback_data("CANCEL", callback_key=callback_key)))
        row.append(
            InlineKeyboardButton(
                done_button_message, callback_data=FoodCourtSelectingHandler.create_callback_data("DONE", callback_key=callback_key)))
        keyboard.append(row)

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def create_callback_data(action: str, food_court_id: str = "-", callback_key: str = "FOODCOURT") -> str:
        return callback_key + ";" + ";".join([action, food_court_id])

    @staticmethod
    def separate_callback_data(data: str) -> list:
        return data.split(";")