from typing import Optional

import logging
import json

from aiotg import Chat

from tg_notificator.tg_bot_base import BotCommand, TgBotBase, InlineKeyboardMarkupData, InlineKeyboardButtonData

log = logging.getLogger(__name__)


class EchoCommand(BotCommand):
    async def run(self, initial_message: Chat):
        await self.send_message(
            f"Your message in API format\n"
            f"```\n"
            f"{json.dumps(initial_message.message, indent=2)}"
            f"```"
        )


class RemindCommand(BotCommand):
    async def request_date(self):
        day = 1
        result = await self.send_message("Select date")
        msg_id = result["result"]["message_id"]

        while True:
            result = await self.edit_message_reply_markup(msg_id, markup=InlineKeyboardMarkupData(inline_keyboard=[
                [
                    InlineKeyboardButtonData(text="-", callback_data="day_dec"),
                    InlineKeyboardButtonData(text=f"{day}", callback_data="day_click"),
                    InlineKeyboardButtonData(text="+", callback_data="day_inc"),
                ]
            ]))
            log.info(result)

            cq = await self.next_callback()
            log.info(f"CQ {cq}")

            if cq.data == "day_inc":
                day += 1
            elif cq.data == "day_dec":
                day -= 1
            else:
                break

            await self.answer_callback_query(cq)

        await self.answer_callback_query(cq)
        await self.edit_message_reply_markup(msg_id, InlineKeyboardMarkupData(inline_keyboard=[[]]))
        return day

    async def run(self, initial_message: Chat):
        initial_text = initial_message.message["text"]  # type: str

        if len(initial_text.split()) > 1:
            reminder_text = " ".join(initial_text.split()[1:])
        else:
            await self.send_message("Что напомнить?")

            remind_text_message = await self.next_message()

            reminder_text = remind_text_message.message["text"]

        await self.send_message(text=f"Ок. Напомню: {reminder_text}")

        date = await self.request_date()

        await self.send_message(f"Напомню в {date}")
        # while True:
        #     msg = await self.next_message()
        #     print(msg.message)


class TgBot(TgBotBase):
    def _dispatch_initial_message(self, chat_obj) -> Optional[BotCommand]:
        msg = chat_obj.message["text"]  # type: str

        if msg.lower().startswith("echo"):
            return EchoCommand(self.app_wrapper.loop, chat_obj)
        elif msg.lower().startswith("remind"):
            return RemindCommand(self.app_wrapper.loop, chat_obj)
