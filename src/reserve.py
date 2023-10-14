import threading
from telegram import ReplyKeyboardMarkup
from src.automatic_reserve_handler import AutomaticReserveHandler
from src.inline_keyboards_handlers.automatic_reserve_already_activated_handler import (
    AutomaticReserveAlreadyActivatedHandler)
from src.inline_keyboards_handlers.choose_food_courts_handler import (
    FoodCourtSelectingHandler)
from src.inline_keyboards_handlers.food_priorities_handler import (
    FoodPrioritiesHandler)
from src.inline_keyboards_handlers.choose_reserve_days_food_court_handler import (
    ChooseReserveDaysFoodCourtHandler)
from src.dining import Dining
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

    async def update_user_favorite_foods(self, update, context):
        context.user_data['priorities'] = []
        await self.show_favorite_foods(update, context)
        await update.message.reply_text(
            text=messages.choose_food_priorities_message,
            reply_markup=FoodPrioritiesHandler.create_food_list_keyboard(
                foods=self.foods_with_id, page=1)
        )

    async def show_favorite_foods(self, update, context):
        user_priorities = self.db.get_user_food_priorities(update.message.chat.id)
        if user_priorities:
            user_priorities = [self.food_name_by_id.get(food) for food in user_priorities]
            await context.bot.send_message(
                update.message.chat.id,
                messages.favorite_foods_list.format("🍕" + "\n🍕".join(user_priorities))
            )
        else:
            await context.bot.send_message(
                update.message.chat.id,
                messages.no_favorite_foods_list
            ) 

    async def automatic_reserve(self, context, user_id: str = None, admin_user_id: str = None):
        await AutomaticReserveHandler(self, db=self.db).automatic_reserve(context, user_id, admin_user_id)

    def load_foods(self):
        # Load foods to cache
        for food in self.db.get_all_foods(name=True, id=True):
            self.foods.add(food['name'])
            self.foods_with_id.append((food['id'], food['name']))
            self.food_name_by_id[food['id']] = food['name']
            self.food_id_by_name[food['name']] = food['id']
        logging.info(f"Loaded {len(self.foods)} foods")

    def update_food_lists_caches(self):
        all_foods = self.db.get_all_foods(name=True, id=True)
        self.foods_with_id = []
        for food in all_foods:
            self.foods_with_id.append((food['id'], food['name']))
            self.food_name_by_id[food['id']] = food['name']
            self.food_id_by_name[food['name']] = food['id']

    async def update_food_list(self, update, context, week_number: int):
        dining = Dining(self.admin_username, self.admin_password)
        self.load_foods()
        new_foods = []
        food_id = num_foods = len(self.foods)
        for place_id in static_data.PLACES.values():
            table = dining.get_foods_list(place_id, week_number)
            new_foods = list(set(table) - self.foods)
            if not table: 
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=messages.no_food_found_message.format(static_data.PLACES_NAME_BY_ID.get(str(place_id)))
                )
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=messages.new_food_found.format(len(new_foods), static_data.PLACES_NAME_BY_ID.get(str(place_id)))
                )
            for food_name in new_foods:
                food_id += 1
                self.db.add_food({"name": food_name, "id": str(food_id)})
                logging.debug("Added food: {} {}".format(food_name, food_id))
            self.foods.update(table)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=messages.update_food_list_result.format(len(self.foods) - num_foods))
        logging.info(f"{len(self.foods) - num_foods} foods added")
        threading.Thread(target=self.update_food_lists_caches, args=()).start()
        logging.info("Updated food list in cache started")

    async def inline_food_choosing_handler(self, update, context, action, choosed, page: int):
        query = update.callback_query
        logging.debug("Process choosed action or food: {} {}".format(action, choosed))
        if action == "NEXT":
            await context.bot.edit_message_text(
                text=query.message.text,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                reply_markup=FoodPrioritiesHandler.create_food_list_keyboard(foods=self.foods_with_id, page=page + 1))
        elif action == "PREV":
            await context.bot.edit_message_text(
                text=query.message.text,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                reply_markup=FoodPrioritiesHandler.create_food_list_keyboard(foods=self.foods_with_id, page=page - 1))
        elif action == "SELECT":
            if not context.user_data.get('priorities'):
                context.user_data['priorities'] = []
            context.user_data.get('priorities').append(choosed)
            await context.bot.send_message(
                text=self.food_name_by_id[choosed],
                chat_id=update.effective_chat.id
            )
        elif action == "DONE":
            self.db.set_user_food_priorities(update.effective_chat.id, context.user_data.get('priorities'))
            if context.user_data: context.user_data.clear()
            await context.bot.edit_message_text(
                text=messages.choosing_food_priorities_done_message,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)
            return static_data.RESERVE_MENU_CHOOSING
        elif action == "CANCEL":
            if context.user_data: context.user_data.clear()
            await context.bot.edit_message_text(
                text=messages.choosing_food_priorities_cancel_message,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)     
            return static_data.RESERVE_MENU_CHOOSING
        elif action == "IGNORE":
            await context.bot.answer_callback_query(callback_query_id=query.id)

    async def set_username_and_password_handler(self, update, context):
        if self.db.get_user_login_info(update.message.chat.id).get('password'):
            await update.message.reply_text(
                text=messages.login_info_already_set_message,
                reply_markup=ReplyKeyboardMarkup(static_data.BACK_TO_MAIN_MENU_CHOICES)
            )
        await update.message.reply_text(
            text=messages.get_username_message,
            reply_markup=ReplyKeyboardMarkup(static_data.BACK_TO_MAIN_MENU_CHOICES)
        )
        return static_data.INPUT_USERNAME

    async def handle_username_input(self, update, context):
        username = update.message.text
        await update.message.reply_text(
            text=messages.get_password_message,
            reply_markup=ReplyKeyboardMarkup(static_data.BACK_TO_MAIN_MENU_CHOICES)
        )
        context.user_data['username'] = username
        return static_data.INPUT_PASSWORD

    async def handle_password_input(self, update, context):
        password = update.message.text
        message_id = (await update.message.reply_text(messages.username_and_password_saved_message)).message_id
        if not Dining.check_username_and_password(context.user_data['username'], password):
            await context.bot.edit_message_text(
                text=messages.username_or_password_incorrect_message,
                chat_id=update.message.chat_id,
                message_id=message_id,
            )
        else:
            await context.bot.edit_message_text(
                text=messages.username_and_password_correct_message,
                chat_id=update.message.chat_id,
                message_id=message_id,
            )
            self.db.update_user_info({
                "user_id": update.message.chat.id,
                "username": update.effective_user.username,
                "student_number": context.user_data['username'],
                "password": password})
        await self.send_reserve_menu(update, context)
        return static_data.RESERVE_MENU_CHOOSING

    async def activate_automatic_reserve_handler(self, update, context):
        if self.db.get_automatic_reserve_status(update.message.chat.id):
            await update.message.reply_text(
                text=messages.automatic_reserve_already_activated_message,
                reply_markup=AutomaticReserveAlreadyActivatedHandler.create_keyboard()
            )
            return
        message_id = (await update.message.reply_text(messages.activate_automatic_reserve_started_message)).message_id
        user_login_info = self.db.get_user_login_info(update.effective_chat.id)
        if not user_login_info:
            await update.message.reply_text(
                text=messages.no_user_info_message,
            )
            return static_data.RESERVE_MENU_CHOOSING
        dining = Dining(user_login_info['student_number'], user_login_info['password'])
        context.user_data['food_courts'] = []
        food_courts = dining.get_user_food_courts()
        if not food_courts:
            await context.bot.edit_message_text(
                text=messages.no_food_court_found_message,
                chat_id=update.message.chat_id,
                message_id=message_id,
            )
            return
        await context.bot.edit_message_text(
            text=messages.choose_food_courts_to_automatic_reserve_message,
            chat_id=update.message.chat_id,
            message_id=message_id,
            reply_markup=FoodCourtSelectingHandler.create_food_courts_keyboard(food_courts)
        )

    async def reserve_next_week_food(self, update, context):
        await update.message.reply_text(
            text=messages.still_under_struction,
        )
        return static_data.RESERVE_MENU_CHOOSING

    async def send_reserve_menu(self, update, context):
        # await update.message.reply_text(
        #     text=messages.still_under_struction,
        # )
        # return static_data.MAIN_MENU_CHOOSING
        await update.message.reply_text(
            text=messages.reserve_menu_messsage,
            reply_markup=ReplyKeyboardMarkup(static_data.RESERVE_MENU_CHOICES),
        )
        return static_data.RESERVE_MENU_CHOOSING

    async def choose_days_to_reserve(self, update, context):
        user_info = self.db.get_user_food_courts_with_automatic_reserve(update.effective_chat.id)
        if not user_info['automatic_reserve']:
            await update.message.reply_text(
                text=messages.automatic_reserve_not_enabled_message,
                reply_markup=ReplyKeyboardMarkup(static_data.RESERVE_MENU_CHOICES)
            )
            return static_data.RESERVE_MENU_CHOOSING
        else:
            user_food_courts = dict([
                (static_data.PLACES_NAME_BY_ID[food_court_id], food_court_id) for food_court_id in user_info.get('food_courts', [])
            ])
            await update.message.reply_text(
                text=messages.choose_days_to_reserve_message,
                reply_markup=ChooseReserveDaysFoodCourtHandler.create_food_list_keyboard(user_food_courts)
            )
            
        return static_data.CHOOSE_RESERVE_DAYS_FOOD_COURT

    async def inline_food_court_choosing_handler(self, update, context, action, choosed):
        query = update.callback_query
        logging.debug("Process choosed action or food: {} {}".format(action, choosed))
        if action == "SELECT":
            if not context.user_data.get('food_courts'):
                context.user_data['food_courts'] = []
            context.user_data['food_courts'].append(choosed)
            await context.bot.send_message(
                text=static_data.PLACES_NAME_BY_ID.get(choosed, messages.food_court_not_found_message),
                chat_id=update.effective_chat.id
            )
        elif action == "DONE":
            if not context.user_data.get('food_courts'):
                await context.bot.send_message(
                    text=messages.no_food_court_choosed_message,
                    chat_id=update.effective_chat.id
                )
                return
            self.db.set_user_food_courts(update.effective_chat.id, context.user_data.get('food_courts', []))
            await context.bot.edit_message_text(
                text=messages.choosing_food_courts_done_message,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)
            return static_data.RESERVE_MENU_CHOOSING
        elif action == "CANCEL":
            if context.user_data: context.user_data.clear()
            await context.bot.edit_message_text(
                text=messages.choosing_food_courts_cancel_message,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)     
            return static_data.RESERVE_MENU_CHOOSING

    async def inline_choosing_days_food_court_choosing_handler(self, update, context, action, choosed_food_court):
        query = update.callback_query
        logging.debug("Process choosed action or food: {} {}".format(action, choosed_food_court))
        if action == "SELECT":
            context.user_data['choosed_days'] = \
                context.user_data.get('choosed_days', {})[choosed_food_court] = {} 
            await context.bot.send_message(
                text=static_data.PLACES_NAME_BY_ID.get(choosed_food_court, messages.food_court_not_found_message),
                chat_id=update.effective_chat.id
            )
            await context.bot.edit_message_text(
                text=messages.choose_days_after_choosed_food_court_message.format(
                    static_data.PLACES_NAME_BY_ID[choosed_food_court]
                ),
                chat_id=query.message.chat_id,
                message_id=query.message.message_id
            )
            return static_data.CHOOSE_RESERVE_DAYS
        elif action == "CANCEL":
            if context.user_data: context.user_data.clear()
            await context.bot.edit_message_text(
                text=messages.choosing_food_courts_cancel_message,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)     
            return static_data.RESERVE_MENU_CHOOSING
        elif action == "DONE":
            if not context.user_data.get('food_courts'):
                await context.bot.send_message(
                    text=messages.no_reserve_day_choosed_message,
                    chat_id=update.effective_chat.id
                )
                return
            self.db.set_user_reserve_days(update.effective_chat.id, context.user_data.get('choosed_days', {}))
            await context.bot.edit_message_text(
                text=messages.seting_reserve_days_done_message,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)
            return static_data.RESERVE_MENU_CHOOSING

    async def inline_already_activated_handler(self, update, context, action):
        query = update.callback_query
        logging.debug("Process choosed action: {}".format(action))
        if action == "DEACTIVATE":
            self.db.set_automatic_reserve_status(update.effective_chat.id, False)
            await context.bot.edit_message_text(
                text=messages.automatic_reserve_deactivated_message,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id
            )
        elif action == "CHANGE_FOOD_COURTS":
            user_login_info = self.db.get_user_login_info(update.effective_chat.id)
            if not user_login_info:
                await context.bot.send_message(
                    text=messages.no_user_info_message,
                    chat_id=query.message.chat_id,
                )
                return static_data.RESERVE_MENU_CHOOSING
            await context.bot.edit_message_text(
                text=messages.activate_automatic_reserve_started_message,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
            )
            dining = Dining(user_login_info['student_number'], user_login_info['password'])
            context.user_data['food_courts'] = []
            food_courts = dining.get_user_food_courts()
            if not food_courts:
                await context.bot.edit_message_text(
                    text=messages.no_food_court_found_message,
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                )
            await context.bot.edit_message_text(
                text=messages.choose_food_courts_to_automatic_reserve_message,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                reply_markup=FoodCourtSelectingHandler.create_food_courts_keyboard(food_courts)
            )
        elif action == "CANCEL":
            if context.user_data: context.user_data.clear()
            await context.bot.edit_message_text(
                text=messages.choosing_food_courts_cancel_message,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)     
            return static_data.RESERVE_MENU_CHOOSING