import logging
from random import randint
from src import messages, static_data
from src.dining import Dining
from telegram.ext import Updater


class AutomaticReserveHandler:
    def __init__(self, token="TOKEN", db=None) -> None:
        self.db = db
        self.token = token

    def automatic_reserve(self, context=None):
        if not context:
            bot = Updater(token=self.token, use_context=True).bot
        else: bot = context.bot
        logging.info("Automatic reserve started")
        users = self.db.get_users_with_automatic_reserve()
        for user in list(users):
            for place_id in user['food_courts']:
                res = self.reserve_next_week_food_based_on_user_priorities(user['user_id'], place_id, user['priorities'], user['student_number'], user['password'])
                if res and all(res):
                    bot.send_message(
                        chat_id=user['user_id'],
                        text=messages.reserve_was_secceeded_message.format(static_data.PLACES_NAME_BY_ID[place_id]))
                else:
                    bot.send_message(
                        chat_id=user['user_id'],
                        text=messages.reserve_was_failed_message.format(static_data.PLACES_NAME_BY_ID[place_id]))
        logging.info("Automatic reserve finished")

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