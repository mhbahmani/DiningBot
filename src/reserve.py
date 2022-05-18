import threading
from telegram import ReplyKeyboardMarkup
from src.dining import Dining
from src.food_priorities_handler import FoodPrioritiesHandler
import src.messages as messages
import src.static_data as static_data
import logging


class ReserveMenuHandler:
    def __init__(self, db_client, admin_sso_username, admin_sso_password) -> None:
        self.db = db_client
        self.admin_username = admin_sso_username
        self.admin_password = admin_sso_password

        self.foods = set()
        self.foods_with_id = []
        self.food_name_by_id = {}

    def update_user_favorite_foods(self, update, context):
        context.user_data['priorities'] = []
        update.message.reply_text(
            text=messages.choose_food_priorities_message,
            reply_markup=FoodPrioritiesHandler.create_food_list_keyboard(
                foods=self.foods_with_id, page=1)
        )

    def load_foods(self):
        for food in self.db.get_all_foods(name=True, id=True):
            self.foods.add(food['name'])
            self.foods_with_id.append((food['id'], food['name']))
            self.food_name_by_id[food['id']] = food['name']
        logging.info(f"Loaded {len(self.foods)} foods")

    def update_food_lists_caches(self):
        for food in self.db.get_all_foods(name=True, id=True):
            self.foods_with_id.append((food['id'], food['name']))
            self.food_name_by_id[food['id']] = food['name']

    def update_food_list(self, update, context, week_number: int):
        self.dining = Dining(self.admin_username, self.admin_password)
        new_foods = []
        food_id = num_foods = len(self.foods)
        for place_id in static_data.PLACES.values():
            table = self.dining.get_foods_list(place_id, week_number)
            if not table: 
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=messages.no_food_found_message
                )
            new_foods = list(set(table) - self.foods)
            for food_name in new_foods:
                food_id += 1
                self.db.add_food({"name": food_name, "id": str(food_id)})
                logging.debug("Added food: {} {}".format(food_name, food_id))
            self.foods.update(table)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=messages.update_food_list_result.format(len(self.foods) - num_foods))
        logging.info(f"{len(self.foods) - num_foods} foods added")
        threading.Thread(target=self.update_food_lists_caches, args=()).start()
        logging.info("Updated food list in cache started")

    def inline_food_choosing_handler(self, update, context, action, choosed, page: int):
        query = update.callback_query
        logging.debug("Process choosed action or food: {} {}".format(action, choosed))
        if action == "NEXT":
            context.bot.edit_message_text(
                text=query.message.text,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                reply_markup=FoodPrioritiesHandler.create_food_list_keyboard(foods=self.foods_with_id, page=page + 1))
        elif action == "PREV":
            context.bot.edit_message_text(
                text=query.message.text,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                reply_markup=FoodPrioritiesHandler.create_food_list_keyboard(foods=self.foods_with_id, page=page - 1))
        elif action == "SELECT":
            context.user_data.get('priorities').append(choosed)
            context.bot.send_message(
                text=self.food_name_by_id[choosed],
                chat_id=update.effective_chat.id
            )
        elif action == "DONE":
            self.db.set_user_food_priorities(update.effective_chat.id, context.user_data.get('priorities'))
            context.user_data['priorities'].clear()
            context.bot.edit_message_text(
                text=messages.choosing_food_priorities_done_message,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)
            return static_data.RESERVE_MENU_CHOOSING
        elif action == "CANCEL":
            context.user_data['priorities'].clear()
            context.bot.edit_message_text(
                text=messages.choosing_food_priorities_cancel_message,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)     
            return static_data.RESERVE_MENU_CHOOSING
        elif action == "IGNORE":
            context.bot.answer_callback_query(callback_query_id=query.id)

    def reserve_next_week_food(self, update, context):
        update.message.reply_text(
            text=messages.still_under_struction,
        )
        return static_data.RESERVE_MENU_CHOOSING

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
