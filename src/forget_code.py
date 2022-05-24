from random import randint
from src.utils import get_food_court_id_by_name, make_forget_code_statistics_message
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import src.messages as messages
import src.static_data as static_data


class ForgetCodeMenuHandler:
    FORGET_CODE_LENGTH = 7

    def __init__(self, db_client) -> None:
        self.db = db_client
        self.markup = ReplyKeyboardMarkup(static_data.SELFS)

    def send_forget_code_menu(self, update, context):
        update.message.reply_text(
            text=messages.forget_code_menu_message,
            reply_markup=ReplyKeyboardMarkup(static_data.FORGET_CODE_MENU_CHOICES),
        )
        return static_data.FORGET_CODE_MENU_CHOOSING

    def send_choose_food_court_menu_to_get(self, update, context):
        if self.db.get_user_current_forget_code(update.effective_user.id):
            update.message.reply_text(
                text=messages.you_already_have_forget_code_message,
            )
            return static_data.MAIN_MENU_CHOOSING
        update.message.reply_text(
            text=messages.choose_food_court_message_to_get,
            reply_markup=self.markup,
        )
        return static_data.CHOOSING_SELF_TO_GET

    def send_choose_food_court_menu_to_give(self, update, context):
        update.message.reply_text(
            text=messages.choose_food_court_message_to_give,
            reply_markup=self.markup,
        )
        return static_data.CHOOSING_SELF_TO_GIVE

    def handle_choosed_food_court_to_get(self, update, context):
        choosed_food_court = update.message.text
        forget_codes = list(self.db.find_forget_code(get_food_court_id_by_name(choosed_food_court)))
        if not forget_codes:
            update.message.reply_text(
                text=messages.no_code_for_this_food_court_message
            )
            return self.send_choose_food_court_menu_to_get(update, context)
        # Assign random code to user
        forget_code = forget_codes[randint(0, len(forget_codes) - 1)]
        update.message.reply_text(
            text=messages.forget_code_founded_message.format(forget_code.get("forget_code"), choosed_food_court, forget_code.get("food_name"), forget_code.get("username")),
            reply_markup=self.make_return_forget_code_button(forget_code.get("forget_code"))
        )
        context.bot.send_message(
            chat_id=forget_code.get("user_id"),
            text=messages.someone_took_your_code_message
        )
        self.db.set_forget_code_for_user(update.effective_user.id, forget_code.get("forget_code"))
        self.db.update_forget_code_assignment_status(forget_code.get("forget_code"), True)
        self.back_to_main_menu(update)
        return static_data.MAIN_MENU_CHOOSING

    def handle_choosed_food_court_to_give(self, update, context):
        choosed_food_court = update.message.text
        context.user_data['food_court'] = choosed_food_court
        update.message.reply_text(
            text=messages.get_forget_code_from_user_message,
            reply_markup=ReplyKeyboardMarkup(static_data.BACK_TO_MAIN_MENU_CHOICES)
        )
        return static_data.INPUT_FORGET_CODE

    def handle_forget_code_input(self, update, context):
        forget_code = update.message.text
        if len(forget_code) < ForgetCodeMenuHandler.FORGET_CODE_LENGTH:
            update.message.reply_text(
                text=messages.not_enough_number_error_message
            )
            return static_data.INPUT_FORGET_CODE
        try:
            forget_code = int(forget_code)
        except ValueError:
            update.message.reply_text(
                text=messages.not_int_code_error_message
            )
            return static_data.INPUT_FORGET_CODE
        if not context.user_data['food_court']:
            update.message.reply_text(
                text=messages.food_court_not_choosed_error_message
            )
            return static_data.CHOOSING_SELF_TO_GIVE
        context.user_data['forget_code'] = forget_code
        update.message.reply_text(
            text=messages.get_food_name_message
        )
        return static_data.INPUT_FOOD_NAME
    
    def handle_forget_code_food_name_input(self, update, context):
        self.db.add_forget_code({
            "username": update.effective_user.username,
            "user_id": update.message.chat.id,
            "forget_code": context.user_data['forget_code'],
            "food_name": update.message.text,
            "food_court_id": get_food_court_id_by_name(context.user_data['food_court']),
            "assigned": False,
            "assigned_to_user_id": update.effective_user.id,
            "asssigned_to_username": update.effective_user.username
        })
        update.message.reply_text(
            text=messages.forget_code_added_message
        )
        if context.user_data: context.user_data.clear()
        self.back_to_main_menu(update)
        return static_data.MAIN_MENU_CHOOSING

    def send_forget_code_ranking(self, update, context):
        users = list(self.db.get_users_forget_code_counts())
        if users:
            users = users[:50]
        else:
            update.message.reply_text(
                text=messages.no_one_added_code_yet_message
            )
            return static_data.FORGET_CODE_MENU_CHOOSING
        message = ""
        for i, user in enumerate(users):
            message += messages.ranking_message.format(i + 1, user.get("username"), user.get("count"))
        message += messages.user_rank_message.format(
            self.db.get_user_rank(update.effective_user.id).get('rank', messages.rank_not_found_message),
            self.db.get_num_users())
        update.message.reply_text(
            text=messages.users_ranking_message.format(message)
        )
        return static_data.FORGET_CODE_MENU_CHOOSING

    def back_to_main_menu(self, update):
        update.message.reply_text(
            text=messages.main_menu_message,
            reply_markup=ReplyKeyboardMarkup(static_data.MAIN_MENU_CHOICES),
        )
    
    def inline_return_forget_code_handler(self, update, context, forget_code: int):
        self.db.update_forget_code_assignment_status(forget_code, False)
        context.bot.edit_message_text(
            text=messages.forget_taked_back_message,
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id
        )
        self.db.set_forget_code_for_user(update.effective_user.id, None)

    def get_fake_forget_code(self, update, context):
        update.message.reply_text(
            text=messages.fake_forget_code_report_message,
            reply_markup=ReplyKeyboardMarkup(static_data.BACK_TO_MAIN_MENU_CHOICES),
        )
        return static_data.INPUT_FAKE_FORGET_CODE

    def forget_code_statistics(self, update, context):
        update.message.reply_text(
            text=make_forget_code_statistics_message(self.db.get_forget_codes_by_food_court_id()))
        return static_data.FORGET_CODE_MENU_CHOOSING

    def handle_fake_forget_code_input(self, update, context):
        fake_forget_code = update.message.text
        if len(fake_forget_code) < ForgetCodeMenuHandler.FORGET_CODE_LENGTH:
            update.message.reply_text(
                text=messages.not_enough_number_error_message
            )
            return static_data.INPUT_FAKE_FORGET_CODE
        try:
            fake_forget_code = int(fake_forget_code)
        except ValueError:
            update.message.reply_text(
                text=messages.not_int_code_error_message
            )
            return static_data.INPUT_FAKE_FORGET_CODE
        forget_code = self.db.get_forget_code_info(fake_forget_code)
        # TODO
        update.message.reply_text(
            text=messages.fake_forget_code_taked_message,
        )
        self.back_to_main_menu(update)
        return static_data.MAIN_MENU_CHOOSING
    
    def make_return_forget_code_button(self, forget_code):
        return InlineKeyboardMarkup([[InlineKeyboardButton(
                    messages.i_dont_want_this_code_message,
                    callback_data=ForgetCodeMenuHandler.create_callback_data(forget_code))]])

    @staticmethod
    def create_callback_data(forget_code) -> str:
        return "FORGETCODE" + ";" + ";".join([str(forget_code)])

    @staticmethod
    def separate_callback_data(data: str) -> list:
        return data.split(";")