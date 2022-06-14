import html
import json
import logging
import traceback
import sentry_sdk

from telegram import Update

import src.messages as messages


class ErrorHandler:
    NOT_ALLOWED_TO_RESERVATION_PAGE_ERROR = "User is not allowed to access reservation page"

    def __init__(self, admin_ids=set(), sentry_dsn: str = None, environment: str = "development") -> None:
        self.admin_ids = admin_ids
        sentry_sdk.init(
            sentry_dsn,
            traces_sample_rate=1.0,
            environment=environment
        )


    def handle_error(self, update, context) -> None:
        """Log the error and send a telegram message to notify the developer."""
        self.send_error_message_to_user(update, context)

        logging.error(msg="Exception while handling an update", exc_info=context.error)

        # traceback.format_exception returns the usual python message about an exception, but as a
        # list of strings rather than a single string, so we have to join them together.
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)

        update_str = update.to_dict() if isinstance(update, Update) else str(update)
        
        # message = (
        #     f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}</pre>\n"
        #     f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>"
        # )
        message = (
            f"<pre>text: {update.message.text}</pre>\n"
            f"<pre>username: {update.message.chat.username}</pre>\n"
            f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>"
        )
        # send the message to admin
        for admin_id in self.admin_ids:
            context.bot.send_message(
                chat_id=admin_id,
                text=message,
                parse_mode="HTML"
            )

        # message = (
        #     f"<pre>{html.escape(tb_string)}</pre>"
        # )
        # send the message to admin
        # for admin_id in self.admin_ids:
        #     context.bot.send_message(
        #         chat_id=admin_id,
        #         text=message,
        #         parse_mode="HTML"
        #     )

    def send_error_message_to_user(self, update, context) -> None:
        """Send a telegram message to notify the user that an error occurred."""
        if not context.error.args: return
        chat_id = None
        if update.callback_query: chat_id = update.callback_query.message.chat_id
        elif update.message: chat_id = update.message.chat_id
        if context.error.args[0] == ErrorHandler.NOT_ALLOWED_TO_RESERVATION_PAGE_ERROR:
            context.bot.send_message(
                text=messages.not_allowed_to_reserve_message,
                chat_id=chat_id
            )