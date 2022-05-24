from random import randint
import threading
from src import messages, static_data
from src.dining import Dining
from telegram.ext import Updater

import logging
import re


class AutomaticReserveHandler:
    def __init__(self, token="TOKEN", admin_ids=set(), log_level=logging.INFO, db=None) -> None:
        self.db = db
        self.token = token
        self.admin_ids = admin_ids

        self.food_name_by_id = {}
        self.food_id_by_name = {}

        logging.basicConfig(
            format='%(asctime)s - %(levelname)s - %(message)s',
            level={
                'INFO': logging.INFO,
                'DEBUG': logging.DEBUG,
                'ERROR': logging.ERROR,
            }[log_level])

        self.load_foods()
    
    def load_foods(self):
        for food in self.db.get_all_foods(name=True, id=True):
            self.food_name_by_id[food['id']] = food['name']
            self.food_id_by_name[food['name']] = food['id']
        logging.info(f"Loaded {len(self.food_id_by_name)} foods")

    def automatic_reserve(self, context=None, user_id: str = None):
        if not context:
            if not self.token: return
            bot = Updater(token=self.token, use_context=True).bot
        else: bot = context.bot
        logging.info("Automatic reserve started")
        users = self.db.get_user_reserve_info(user_id) if user_id else self.db.get_users_with_automatic_reserve()
        for user in list(users):
            successfull_reserve = True
            for place_id in user['food_courts']:
                reserve_successes, foods = self.reserve_next_week_food_based_on_user_priorities(user['user_id'], place_id, user['priorities'], user['student_number'], user['password'])
                if reserve_successes and all(reserve_successes):
                    bot.send_message(
                        chat_id=user['user_id'],
                        text=messages.reserve_was_secceeded_message.format(
                            static_data.PLACES_NAME_BY_ID[place_id], self.beautify_reserved_foods_output(foods)))
                else:
                    bot.send_message(
                        chat_id=user['user_id'],
                        text=messages.reserve_was_failed_message.format(static_data.PLACES_NAME_BY_ID[place_id]))
                    successfull_reserve = False
            if successfull_reserve:
                threading.Thread(target=self.db.set_user_next_week_reserve_status, args=(user['user_id'], True)).start()
        logging.info("Automatic reserve finished")

    def reserve_next_week_food_based_on_user_priorities(self, user_id: str, place_id, user_priorities: list, username, password):
        logging.debug("Reserving food for user {} at {}".format(user_id, static_data.PLACES_NAME_BY_ID[place_id]))
        dining = Dining(username, password)
        foods = dining.get_reserve_table_foods(place_id, week=1)
        reserve_successes = []
        food_names = []
        for day in foods:
            for meal in dining.meals:
                if not foods[day][meal]: continue
                day_foods = list(map(lambda food: self.food_id_by_name.get(food.get("food")), foods[day][meal]))
                if not day_foods: continue
                choosed_food_id = foods[day][meal][0].get("food_id")
                food_index_in_foods_list = 0
                if len(day_foods) > 1:
                    choosed_food_index = min(map(lambda x: user_priorities.index(x) if x in user_priorities else 100, day_foods))
                    if choosed_food_index == 100: food_index_in_foods_list = randint(0, len(day_foods) - 1)
                    else: food_index_in_foods_list = day_foods.index(user_priorities[choosed_food_index])
                choosed_food_id = foods[day][meal][food_index_in_foods_list]['food_id']
                reserve_success, balance = dining.reserve_food(int(place_id), int(choosed_food_id))
                reserve_successes.append(reserve_success)
                food_names.append((foods[day][meal][food_index_in_foods_list].get('food'), day))
        return reserve_successes, food_names

    def beautify_reserved_foods_output(self, food_names: list) -> str:
        food_names.reverse()
        return "\n".join(list(
            map(
                lambda x: messages.list_reserved_foods_message.format(
                    re.sub("\d+\/\d+\/\d+ ", "", x[1]), x[0]), food_names)))