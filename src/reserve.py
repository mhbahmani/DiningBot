from random import randint
import threading
from telegram import ReplyKeyboardMarkup
from src.choose_food_courts_handler import FoodCourtSelectingHandler
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
        self.food_id_by_name = {}

    def update_user_favorite_foods(self, update, context):
        context.user_data['priorities'] = []
        update.message.reply_text(
            text=messages.choose_food_priorities_message,
            reply_markup=FoodPrioritiesHandler.create_food_list_keyboard(
                foods=self.foods_with_id, page=1)
        )

    def automatic_reserve(self, update, context):
        logging.info("Automatic reserve started")
        users = self.db.get_users_with_automatic_reserve()
        for user in list(users):
            for place_id in user['food_courts']:
                res = self.reserve_next_week_food_based_on_user_priorities(user['user_id'], place_id, user['priorities'], user['student_number'], user['password'])
                if res and all(res):
                    context.bot.send_message(
                        chat_id=user['user_id'],
                        text=messages.reserve_was_secceeded_message.format(static_data.PLACES_NAME_BY_ID[place_id])
                    )
                else:
                    context.bot.send_message(
                        chat_id=user['user_id'],
                        text=messages.reserve_was_failed_message.format(static_data.PLACES_NAME_BY_ID[place_id])
                    )
        logging.info("Automatic reserve finished")

    def load_foods(self):
        for food in self.db.get_all_foods(name=True, id=True):
            self.foods.add(food['name'])
            self.foods_with_id.append((food['id'], food['name']))
            self.food_name_by_id[food['id']] = food['name']
            self.food_id_by_name[food['name']] = food['id']
        logging.info(f"Loaded {len(self.foods)} foods")

    def update_food_lists_caches(self):
        for food in self.db.get_all_foods(name=True, id=True):
            self.foods_with_id.append((food['id'], food['name']))
            self.food_name_by_id[food['id']] = food['name']
            self.food_id_by_name[food['name']] = food['id']

    def update_food_list(self, update, context, week_number: int):
        dining = Dining(self.admin_username, self.admin_password)
        new_foods = []
        food_id = num_foods = len(self.foods)
        for place_id in static_data.PLACES.values():
            table = dining.get_foods_list(place_id, week_number)
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

    def reserve_next_week_food_based_on_user_priorities(self, user_id: str, place_id, user_priorities: list, username, password):
        logging.debug("Reserving food for user {}".format(user_id))
        dining = Dining(username, password)
        foods = dining.get_reserve_table_foods(place_id, week=1)
        res = []
        for day in foods:
            for meal in dining.meals:
                if not foods[day][meal]: continue
                day_foods = list(map(lambda food: self.food_id_by_name.get(food.get("food")), foods[day][meal]))
                choosed_food_id = foods[day][meal][0].get("food_id")
                if not day_foods: continue
                if len(day_foods) > 1:
                    choosed_food_index = min(map(lambda x: user_priorities.index(x) if x in user_priorities else 100, day_foods))
                    choosed_food_id = foods[day][meal][day_foods.index(user_priorities[choosed_food_index])]['food_id']
                    if choosed_food_index == 100:
                        choosed_food_id = foods[day][meal][randint(0, len(day_foods) - 1)]['food_id']
                res.append(dining.reserve_food(int(place_id), int(choosed_food_id)))
        return res

    def set_username_and_password_handler(self, update, context):
        update.message.reply_text(
            text=messages.get_username_message,
            reply_markup=ReplyKeyboardMarkup(static_data.BACK_TO_MAIN_MENU_CHOICES)
        )
        return static_data.INPUT_USERNAME

    def handle_username_input(self, update, context):
        username = update.message.text
        update.message.reply_text(
            text=messages.get_password_message,
            reply_markup=ReplyKeyboardMarkup(static_data.BACK_TO_MAIN_MENU_CHOICES)
        )
        context.user_data['username'] = username
        return static_data.INPUT_PASSWORD

    def handle_password_input(self, update, context):
        password = update.message.text
        update.message.reply_text(messages.username_and_password_saved_message)
        if not Dining.check_username_and_password(context.user_data['username'], password):
            update.message.reply_text(messages.username_or_password_incorrect_message)
        else:
            update.message.reply_text(messages.username_and_password_correct_message)
            self.db.update_user_info({
                "user_id": update.message.chat.id,
                "username": update.effective_user.username,
                "student_number": context.user_data['username'],
                "password": password})
        self.send_reserve_menu(update, context)
        return static_data.RESERVE_MENU_CHOOSING

    def activate_automatic_reserve_handler(self, update, context):
        update.message.reply_text(messages.activate_automatic_reserve_started_message)
        user_login_info = self.db.get_user_login_info(update.effective_chat.id)
        if not user_login_info:
            update.message.reply_text(
                text=messages.no_user_info_message,
            )
            return static_data.RESERVE_MENU_CHOOSING
        dining = Dining(user_login_info['student_number'], user_login_info['password'])
        context.user_data['food_courts'] = []
        update.message.reply_text(
            text=messages.choose_food_courts_to_automatic_reserve_message,
            reply_markup=FoodCourtSelectingHandler.create_food_courts_keyboard(dining.get_user_food_courts())
        )

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

    def inline_food_court_choosing_handler(self, update, context, action, choosed):
        query = update.callback_query
        logging.debug("Process choosed action or food: {} {}".format(action, choosed))
        if action == "SELECT":
            context.user_data.get('food_courts').append(choosed)
            context.bot.send_message(
                text=static_data.PLACES_NAME_BY_ID[choosed],
                chat_id=update.effective_chat.id
            )
        elif action == "DONE":
            self.db.set_user_food_courts(update.effective_chat.id, context.user_data.get('food_courts', []))
            context.bot.edit_message_text(
                text=messages.choosing_food_courts_done_message,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)
            return static_data.RESERVE_MENU_CHOOSING
        elif action == "CANCEL":
            context.user_data['priorities'].clear()
            context.bot.edit_message_text(
                text=messages.choosing_food_courts_cancel_message,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)     
            return static_data.RESERVE_MENU_CHOOSING