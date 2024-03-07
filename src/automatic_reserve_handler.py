from random import randint
import threading
from src import messages, static_data
from src.error_handlers import (
    NotEnoughCreditToReserve,
    NoFoodScheduleForUser,
    FoodsCapacityIsOver,
    NoSuchFoodSchedule,
    DiningLoginFailed,
    AlreadyReserved,
    ErrorHandler
)
from src.dining import Dining
from src.rest_dining import Samad
from telegram.ext import ApplicationBuilder
from telegram import error

import logging
import re


class AutomaticReserveHandler:
    def __init__(self, token="TOKEN", admin_ids=set(), log_level='INFO', db=None, sentry_dsn: str = None) -> None:
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

        self.error_handler = ErrorHandler(admin_ids, sentry_dsn)

        self.load_foods()

    def load_foods(self):
        for food in self.db.get_all_foods(name=True, id=True):
            self.food_name_by_id[food['id']] = food['name']
            self.food_id_by_name[food['name']] = food['id']
        logging.info(f"Loaded {len(self.food_id_by_name)} foods")

    async def clean_reservation_status(self):
        self.db.set_all_users_next_week_reserve_status(False)

    async def handle_automatic_reserve(self):
        self.load_foods()
        await self.automatic_reserve()

    async def automatic_reserve(self, context=None, user_id: str = None, admin_user_id: str = None):
        if not context:
            if not self.token: return
            bot = ApplicationBuilder().token(self.token).build().bot
        else:
            bot = context.bot
        logging.info("########### Automatic reserve started ################")
        users = [self.db.get_user_reserve_info(user_id)] if user_id else list(self.db.get_users_with_automatic_reserve())
        logging.info(f"**** Number of users: {len(users)} ****")
        for user in users:
            msg_receiver_id = admin_user_id if admin_user_id else user['user_id']
            reserves = {}
            try:
                for place_id in user['food_courts']:
                    if user.get('food_courts_next_week_reserve', {}).get(str(place_id), False): continue
                    reserve_success = False
                    try:
                        logging.info("Reserving food for user {} at {}".format(user['user_id'], static_data.PLACES_NAME_BY_ID[place_id]))
                        reserve_success, reserved_foods, remain_credit, reserved_days = self.reserve_next_week_food_based_on_user_priorities(
                            place_id,
                            user.get('reserve_days', {}).get(str(place_id), []),
                            user.get('priorities',
                                    []),
                            user['student_number'],
                            user['password']
                        )

                        if reserve_success:
                            reserve_report_message = messages.reserve_was_secceeded_message.format(
                                    static_data.PLACES_NAME_BY_ID[place_id],
                                    self.beautify_reserved_foods_output(reserved_foods, user.get('reserve_days', {}).get(str(place_id), []), reserved_days),
                                    remain_credit)
                            await bot.send_message(
                                chat_id=user['user_id'],
                                text=reserve_report_message)
                            logging.info("Reserve was successfull for user {} at {}, remain credit: {}".format(user['user_id'],
                                                                                            static_data.PLACES_NAME_BY_ID[
                                                                                                place_id], remain_credit))
                        else:
                            # await bot.send_message(
                            #     chat_id=user['user_id'],
                            #     text=messages.reserve_was_failed_message.format(static_data.PLACES_NAME_BY_ID[place_id]))
                            logging.info("Something went wrong for user {} at {}".format(user['user_id'],
                                                                                        static_data.PLACES_NAME_BY_ID[
                                                                                            place_id]))

                    except AlreadyReserved as e:
                        logging.info(e.message)
                        await bot.send_message(
                            chat_id=msg_receiver_id,
                            text=messages.already_reserved_message.format(
                                static_data.PLACES_NAME_BY_ID[place_id]))
                        reserve_success = True
                        # If user has already reserved his food, we should set his food_court_next_week_reserve status to True
                        # Because of the above line, the line below is unnecessary
                        # threading.Thread(target=self.db.set_user_specific_food_court_reserve_status, args=(user['user_id'], place_id, reserve_success)).start()

                    except DiningLoginFailed as e:
                        logging.info(e.message)
                        await bot.send_message(
                            chat_id=msg_receiver_id,
                            text=messages.logind_failed_on_automatic_reserve_message.format(
                                static_data.PLACES_NAME_BY_ID[place_id]))
                    except NotEnoughCreditToReserve as e:
                        logging.info(e.message)
                        await bot.send_message(
                            chat_id=msg_receiver_id,
                            text=messages.not_enough_credit_to_reserve_message.format(
                                static_data.PLACES_NAME_BY_ID[place_id]))
                    except FoodsCapacityIsOver as e:
                        logging.error("Error on reserving food for user {} with message {}".format(user['user_id'], e.message))
                        await bot.send_message(
                            chat_id=msg_receiver_id,
                            text=messages.food_capacity_is_over.format(static_data.PLACES_NAME_BY_ID[place_id]))
                    except NoFoodScheduleForUser as e:
                        logging.error("Error on reserving food for user {} with message {}".format(user['user_id'], e.message))
                        await bot.send_message(
                            chat_id=msg_receiver_id,
                            text=messages.no_food_schedule_on_this_court_for_you_message.format(static_data.PLACES_NAME_BY_ID[place_id]))
                    except NoSuchFoodSchedule as e:
                        logging.error("Error on reserving food for user {} with message {}".format(user['user_id'], e.message))
                        await bot.send_message(
                            chat_id=list(self.admin_ids)[0],
                            # text=messages.reserve_was_failed_message.format(static_data.PLACES_NAME_BY_ID[place_id]))
                            text=messages.reserve_was_failed_message.format(user['user_id'], static_data.PLACES_NAME_BY_ID[place_id], place_id, e))
                    except Exception as e:
                        logging.error("Error on reserving food for user {} with message {}".format(user['user_id'], e))
                        await bot.send_message(
                            chat_id=list(self.admin_ids)[0],
                            # text=messages.reserve_was_failed_message.format(static_data.PLACES_NAME_BY_ID[place_id]))
                            text=messages.reserve_was_failed_message.format(user['user_id'], static_data.PLACES_NAME_BY_ID[place_id], place_id, e))

                    reserves[place_id] = reserve_success

                threading.Thread(target=self.db.set_user_food_court_next_week_reserve_status, args=(user['user_id'], reserves)).start()
                threading.Thread(target=self.db.set_user_next_week_reserve_status, args=(user['user_id'], all(list(reserves.values())))).start()
            except error.Forbidden:
                logging.info(f"User blocked The bot f{user['user_id']}!!!")
                # If user blocked the bot, we should disable the automatic reserve feature for him/her
                threading.Thread(self.db.set_automatic_reserve_status(user["user_id"], False)).start()

        logging.info("################ Automatic reserve finished ################")

    def reserve_next_week_food_based_on_user_priorities(self, place_id, reserve_days: list, user_priorities: list, username,
                                                        password):
        try:
            samad = Samad(username, password)
            if samad.check_user_week_reservation_status(place_id):
                raise(AlreadyReserved)
            dining = Dining(username, password)
        except Exception as e:
            raise(DiningLoginFailed)
        foods = dining.get_reserve_table_foods(place_id)
        choosed_food_indices = {}
        food_names = []
        for day in foods:
            for meal in dining.meals:
                if not foods[day][meal]: continue
                day_foods = list(map(lambda food: self.food_id_by_name.get(food.get("food")), foods[day][meal]))
                if not day_foods: continue
                food_index_in_foods_list = 0
                if len(day_foods) > 1:
                    choosed_food_index = min(
                        map(lambda x: user_priorities.index(x) if x in user_priorities else 100, day_foods))
                    if choosed_food_index == 100:
                        food_index_in_foods_list = randint(0, len(day_foods) - 1)
                    else:
                        food_index_in_foods_list = day_foods.index(user_priorities[choosed_food_index])

                choosed_food_indices[day] = choosed_food_indices.get(day, {})
                choosed_food_indices[day][meal] = food_index_in_foods_list

                food_names.append((foods[day][meal][food_index_in_foods_list].get('food'), day, meal))
        reserved_days, remain_credit = dining.reserve_food(int(place_id), foods, choosed_food_indices, reserve_days)
        return True, food_names, remain_credit, reserved_days

    def beautify_reserved_foods_output(self, food_names: list, choosed_days: list = [], reserved_days: list = []) -> str:
        food_names.reverse()
        reserved_foods = []
        for i, food in enumerate(food_names):
            # If choosed days is empty, the whole week has been reserved
            # If the food day is not in reserved days, continue
            # if choosed_days and not i in choosed_days: continue
            if choosed_days and not " ".join(food[1].split()[1:]) in reserved_days: continue
            reserved_foods.append(
                messages.list_reserved_foods_message.format(re.sub("\d+\/\d+\/\d+ ", "", food[1]), static_data.MEAL_EN_TO_FA.get(food[2], ""), food[0])
            )
        return "\n".join(reserved_foods)

    async def notify_users(self):
        users = self.db.get_users_with_automatic_reserve()
        bot = ApplicationBuilder().token(self.token).build().bot
        for user in users:
            try:
                await bot.send_message(
                    chat_id=user['user_id'],
                    text=messages.automatic_reserve_notification_message
                )
            except error.Forbidden:
                # If user blocked the bot, we should disable the automatic reserve feature for him/her
                threading.Thread(self.db.set_automatic_reserve_status(user["user_id"], False)).start()

    async def notify_users_about_reservation_status(self):
        users = self.db.get_users_with_automatic_reserve()
        bot = ApplicationBuilder().token(self.token).build().bot
        for user in users:
            try:
                await bot.send_message(
                    chat_id=user["user_id"],
                    parse_mode="MarkdownV2",
                    text=messages.you_dont_have_food_for_next_week_message
                )
            except error.Forbidden:
                # If user blocked the bot, we should disable the automatic reserve feature for him/her
                threading.Thread(self.db.set_automatic_reserve_status(user["user_id"], False)).start()
