from typing import Optional

import logging
import json

from aiotg import Chat

from tg_notificator.tg_bot_base import BotCommand, TgBotBase

log = logging.getLogger(__name__)


class EchoCommand(BotCommand):
    async def run(self, initial_message: Chat):
        await initial_message.send_text(
            f"Your message in API format\n"
            f"{json.dumps(initial_message.message, indent=2)}"
        )


class RemindCommand(BotCommand):
    async def run(self, initial_message: Chat):
        initial_text = initial_message.message["text"]  # type: str

        if len(initial_text.split()) > 1:
            reminder_text = " ".join(initial_text.split()[1:])
        else:
            await initial_message.send_text("Что напомнить?")

            remind_text_message = await self.next_message()

            reminder_text = remind_text_message.message["text"]

        await initial_message.send_text(f"Ок. Напомню: {reminder_text}")


class TgBot(TgBotBase):
    def _dispatch_initial_message(self, chat_obj) -> Optional[BotCommand]:
        msg = chat_obj.message["text"]  # type: str

        if msg.lower().startswith("echo"):
            return EchoCommand(self.app_wrapper.loop)
        elif msg.lower().startswith("remind"):
            return RemindCommand(self.app_wrapper.loop)
