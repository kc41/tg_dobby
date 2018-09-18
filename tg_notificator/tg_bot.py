from typing import Optional

from datetime import datetime, timedelta
import logging
import json

import yaml
from aiotg import Chat

from tg_notificator.date_utils import add_months
from tg_notificator.grammar import analyse_natural_date
from tg_notificator.tg_bot_base import BotCommand, TgBotBase, InlineKeyboardMarkupData, InlineKeyboardButtonData, \
    CallbackQueryData, MessageData

log = logging.getLogger(__name__)


class EchoCommand(BotCommand):
    async def run(self, initial_message: Chat):
        await self.send_message(
            f"Your message in API format\n"
            f"```\n"
            f"{json.dumps(initial_message.message, indent=2)}"
            f"```"
        )


class ParseDateCommand(BotCommand):
    async def run(self, initial_message: Chat):
        cancel_submit_markup = InlineKeyboardMarkupData(inline_keyboard=[
            [InlineKeyboardButtonData(text="Отмена", callback_data="submit")]
        ])

        await self.send_message("Что разобрать?", reply_markup=cancel_submit_markup)

        while True:
            upd = await self.next_update()

            if isinstance(upd, MessageData):
                txt = upd.text.lower()

                f = analyse_natural_date(txt)

                if f:
                    await self.send_message(
                        f"```\n"
                        f"{yaml.dump(dict(f.as_json), default_flow_style=False, allow_unicode=True)}\n"
                        f"```",
                        reply_markup=cancel_submit_markup,
                    )
                else:
                    await self.send_message("Не понял 🙁", reply_markup=cancel_submit_markup)

            elif isinstance(upd, CallbackQueryData):
                await self.answer_callback_query(upd)
                return


class RemindCommand(BotCommand):
    async def request_date(self) -> Optional[datetime]:
        dt = datetime.now().replace(second=0, microsecond=0)

        msg_id = (await self.send_message(f"Когда?"))["result"]["message_id"]

        def date_edit_markup():
            return InlineKeyboardMarkupData(inline_keyboard=[
                [
                    InlineKeyboardButtonData(text=dt.strftime("%d %b %Y %H:%M"), callback_data="submit")
                ],
                [
                    InlineKeyboardButtonData(text="-", callback_data="d_dec"),
                    InlineKeyboardButtonData(text=f"{dt.day}", callback_data="d_click"),
                    InlineKeyboardButtonData(text="+", callback_data="d_inc"),
                ],
                [
                    InlineKeyboardButtonData(text="-", callback_data="m_dec"),
                    InlineKeyboardButtonData(text=f"{dt.month}", callback_data="m_click"),
                    InlineKeyboardButtonData(text="+", callback_data="m_inc"),
                ],
            ])

        while True:
            await self.edit_message_reply_markup(msg_id, markup=date_edit_markup())

            upd = await self.next_update()

            if isinstance(upd, MessageData):
                # txt = intr.text.lower()
                msg_id = (await self.send_message(f"Таки когда?"))["result"]["message_id"]

            elif isinstance(upd, CallbackQueryData):
                if upd.data == "d_inc":
                    dt += timedelta(days=1)
                elif upd.data == "d_dec":
                    dt -= timedelta(days=1)

                elif upd.data == "m_inc":
                    dt = add_months(dt, 1)
                elif upd.data == "m_dec":
                    dt = add_months(dt, -1)

                elif upd.data == "submit":
                    await self.answer_callback_query(upd)
                    break

                elif upd.data == "cancel":
                    await self.answer_callback_query(upd)
                    return None

                else:
                    # Ignoring callback data
                    await self.answer_callback_query(upd)

                await self.answer_callback_query(upd)

        # Date received
        await self.edit_message_reply_markup(msg_id, InlineKeyboardMarkupData(inline_keyboard=[[]]))

        return dt

    async def run(self, initial_message: Chat):
        await self.send_message("Что напомнить?")

        remind_text_message = await self.next_message()

        reminder_text = remind_text_message.text

        await self.send_message(text=f"Ок. Напомню: {reminder_text}")

        date = await self.request_date()

        if date:
            await self.send_message(f"Напомню в {date}")
        else:
            await self.send_message(f"Отменено пользователем")


class TgBot(TgBotBase):
    def _dispatch_initial_message(self, chat_obj) -> Optional[BotCommand]:

        msg = chat_obj.message["text"]  # type: str

        if msg == "/echo":
            return EchoCommand(self.app_wrapper.loop, chat_obj)
        elif msg == "/remind":
            return RemindCommand(self.app_wrapper.loop, chat_obj)
        elif msg == "/parse_date":
            return ParseDateCommand(self.app_wrapper.loop, chat_obj)
