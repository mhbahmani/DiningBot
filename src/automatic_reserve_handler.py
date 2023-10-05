from random import randint
import threading
from src import messages, static_data
from src.error_handlers import (
    NotEnoughCreditToReserve,
    NoSuchFoodSchedule
)
from src.dining import Dining
from telegram.ext import Updater
from telegram import error

import logging
import re


class AutomaticReserveHandler:
    def __init__(self, token="TOKEN", admin_ids=set(), log_level='INFO', db=None) -> None:
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

    def clean_reservation_status(self):
        self.db.set_all_users_next_week_reserve_status(False)

    async def handle_automatic_reserve(self):
        await self.automatic_reserve()

    async def automatic_reserve(self, context=None, user_id: str = None):
        if not context:
            if not self.token: return
            bot = Updater(token=self.token, use_context=True).bot
        else:
            bot = context.bot
        logging.info("Automatic reserve started")
        users = [self.db.get_user_reserve_info(user_id)] if user_id else self.db.get_users_with_automatic_reserve()
        reserve_success = False
        for user in list(users):
            for place_id in user['food_courts']:
                try:
                    reserve_success, reserved_foods, remain_credit = self.reserve_next_week_food_based_on_user_priorities(
                        user['user_id'],
                        place_id,
                        user.get('priorities',
                                []),
                        user['student_number'],
                        user['password']
                    )

                except NotEnoughCreditToReserve as e:
                    logging.debug(e.message)
                    await bot.send_message(
                        chat_id=user['user_id'],
                        text=messages.not_enough_credit_to_reserve_message.format(
                            static_data.PLACES_NAME_BY_ID[place_id]))
                except NoSuchFoodSchedule as e:
                    logging.error("Error on reserving food for user {} with message {}".format(user['user_id'], e.message))
                    await bot.send_message(
                        chat_id=user['user_id'],
                        text=messages.reserve_was_failed_message.format(static_data.PLACES_NAME_BY_ID[place_id]))

            if reserve_success:
                await bot.send_message(
                    chat_id=user['user_id'],
                    text=messages.reserve_was_secceeded_message.format(
                        static_data.PLACES_NAME_BY_ID[place_id], self.beautify_reserved_foods_output(reserved_foods), remain_credit))
                logging.info("Reserve was successfull for user {} at {}, remain credit: {}".format(user['user_id'],
                                                                                static_data.PLACES_NAME_BY_ID[
                                                                                    place_id], remain_credit))
                threading.Thread(target=self.db.set_user_next_week_reserve_status, args=(user['user_id'], True)).start()
            else:
                await bot.send_message(
                    chat_id=user['user_id'],
                    text=messages.reserve_was_failed_message.format(static_data.PLACES_NAME_BY_ID[place_id]))
                logging.info("Something went wrong for user {} at {}".format(user['user_id'],
                                                                            static_data.PLACES_NAME_BY_ID[
                                                                                place_id]))
        logging.info("Automatic reserve finished")

    def reserve_next_week_food_based_on_user_priorities(self, user_id: str, place_id, user_priorities: list, username,
                                                        password):
        logging.debug("Reserving food for user {} at {}".format(user_id, static_data.PLACES_NAME_BY_ID[place_id]))
        try:
            dining = Dining(username, password)
        except Exception as e:
            return [False], []
        foods = dining.get_reserve_table_foods(place_id)
        choosed_food_indices = {}
        food_names = []
        for day in foods:
            for meal in dining.meals:
                if not foods[day][meal]: continue
                day_foods = list(map(lambda food: self.food_id_by_name.get(food.get("food")), foods[day][meal]))
                if not day_foods: continue
                choosed_food_id = foods[day][meal][0].get("food_id")
                food_index_in_foods_list = 0
                if len(day_foods) > 1:
                    choosed_food_index = min(
                        map(lambda x: user_priorities.index(x) if x in user_priorities else 100, day_foods))
                    if choosed_food_index == 100:
                        food_index_in_foods_list = randint(0, len(day_foods) - 1)
                    else:
                        food_index_in_foods_list = day_foods.index(user_priorities[choosed_food_index])

                # food_index_in_foods_list = 0 # TODO: Remove This line

                choosed_food_indices[day] = choosed_food_indices.get(day, {})
                choosed_food_indices[day][meal] = food_index_in_foods_list

                # choosed_food_id = foods[day][meal][food_index_in_foods_list]['food_id']
                # TODO: Fix Reserve and the rest
                # reserve_success, balance = dining.reserve_food(int(place_id), int(choosed_food_id))
                # reserve_successes.append(reserve_success)

                food_names.append((foods[day][meal][food_index_in_foods_list].get('food'), day, meal))
        remain_credit = dining.reserve_food(int(place_id), foods, choosed_food_indices)
        return True, food_names, remain_credit

    def beautify_reserved_foods_output(self, food_names: list) -> str:
        food_names.reverse()
        return "\n".join(list(
            map(
                lambda x: messages.list_reserved_foods_message.format(
                    re.sub("\d+\/\d+\/\d+ ", "", x[1]), static_data.MEAL_EN_TO_FA.get(x[2], ""), x[0]), food_names)))

    def notify_users(self):
        users = self.db.get_users_with_automatic_reserve()
        bot = Updater(token=self.token, use_context=True).bot
        for user in users:
            try:
                bot.send_message(
                    chat_id=user['user_id'],
                    text=messages.automatic_reserve_notification_message
                )
            except error.Unauthorized:
                continue

    def notify_users_about_reservation_status(self):
        users = self.db.get_users_with_automatic_reserve()
        bot = Updater(token=self.token, use_context=True).bot
        for user in users:
            try:
                bot.send_message(
                    chat_id=user["user_id"],
                    parse_mode="MarkdownV2",
                    text=messages.you_dont_have_food_for_next_week_message
                )
            except error.Unauthorized:
                continue
