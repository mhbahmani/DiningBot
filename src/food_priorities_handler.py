import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.messages import (
    next_page_button_message,
    previous_page_button_message,
    done_button_message
)


PAGE_SIZE = 10

class FoodPrioritiesHandler:
    @staticmethod
    def create_food_list_keyboard(foods: set, page: int = 1) -> InlineKeyboardMarkup:
        keyboard = []
        foods_list = list(foods)[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]

        while foods_list:
            row = []
            for i in range(2):
                if not foods_list: break
                food = foods_list.pop()
                row.append(
                    InlineKeyboardButton(
                        food,
                        callback_data=FoodPrioritiesHandler.create_callback_data(action="SELECT", food_name=food)))
            keyboard.append(row)

        row = []
        if page > 1:
            row.append(
                InlineKeyboardButton(
                    previous_page_button_message,
                    callback_data=FoodPrioritiesHandler.create_callback_data(action="PREV", food_name="", page=page)))
        else: 
            row.append(
                InlineKeyboardButton(
                    " ", callback_data=FoodPrioritiesHandler.create_callback_data("IGNORE")))
        row.append(
            InlineKeyboardButton(
                done_button_message, callback_data=FoodPrioritiesHandler.create_callback_data("DONE")))
        if len(foods) > page * PAGE_SIZE:
            row.append(
                InlineKeyboardButton(
                    next_page_button_message,
                    callback_data=FoodPrioritiesHandler.create_callback_data(action="NEXT", food_name="", page=page)))
        else: 
            row.append(
                InlineKeyboardButton(
                    " ", callback_data=FoodPrioritiesHandler.create_callback_data("IGNORE")))
        keyboard.append(row)

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def create_callback_data(action: str, food_name: str = "-", page: int = 0) -> str:
        return "FOOD" + ";" + ";".join([action, food_name, str(page)])

    @staticmethod
    def separate_callback_data(data: str) -> list:
        return data.split(";")