from typing import Optional, Iterable, List

from datetime import datetime, timedelta
import logging
import json

import yaml
from aiotg import Chat, asyncio

from tg_dobby.date_utils import add_months
from tg_dobby.grammar import extract_first_natural_date
from tg_dobby.grammar.natural_dates import Moment, RULE_DAY_TIME, DayTime
from tg_dobby.grammar.natural_dates_post_processing import (
    get_absolute_date,
    ClarificationRequired,
    InvalidRelativeDateException,
    ALL_CLARIFICATIONS_CLASSES, DayTimeClarification)
from tg_dobby.grammar.tokenizer import tokenize_phrase, PhraseToken, ReminderPreamble
from tg_dobby.tg_bot_base import (
    BotCommand,
    TgBotBase,
    InlineKeyboardMarkupData,
    InlineKeyboardButtonData,
    CallbackQueryData,
    MessageData,
)

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

                f = extract_first_natural_date(txt)

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


class NaturalReminderCommand(BotCommand):
    REMINDER_PATTERNS = (
        (ReminderPreamble, Moment, type(None),),
        (ReminderPreamble, type(None), Moment,),
        (type(None), Moment,),
        (Moment, type(None)),
    )

    def __init__(self, loop: asyncio.AbstractEventLoop, initial_chat_obj: Chat, initial_tokens: Iterable[PhraseToken]):
        super().__init__(loop, initial_chat_obj)

        token_type_map = {
            type(token.fact): token
            for token in initial_tokens
        }

        self.reminder_text = token_type_map[type(None)].text  # type: str
        self.initial_moment = token_type_map[Moment].fact  # type: Moment

    async def ask_day_time_clarification(self) -> DayTimeClarification:
        await self.send_message("Во сколько?")

        while True:
            response = await self.next_message()

            tokens = tokenize_phrase(response.text, rules=(RULE_DAY_TIME,))

            if len(tokens) == 1:
                fact = tokens[0].fact
                if isinstance(fact, DayTime):
                    return DayTimeClarification(fact)

            await self.send_message("Во сколько, во сколько?")

    async def get_date(self, moment: Moment) -> datetime:
        collected_clarification = []  # type: List[ALL_CLARIFICATIONS_CLASSES]

        # Trying to parse date and collect clarifications if required
        while True:
            try:
                return get_absolute_date(moment, clarifications=collected_clarification)

            except ClarificationRequired as e:

                for required_clarification in e.required_clarifications:
                    if isinstance(required_clarification, DayTimeClarification):
                        c = await self.ask_day_time_clarification()
                        collected_clarification.append(c)

                    else:
                        raise ValueError(f"Unknown clarification type was requested:"
                                         f" {type(required_clarification).__name__}")

    async def run(self, initial_message: Chat):
        # noinspection PyBroadException
        try:
            dt = await self.get_date(self.initial_moment)

            resp_yml = yaml.dump(dict(
                what=self.reminder_text,
                when=dt.strftime('%d %b %Y %H:%M'),

            ), default_flow_style=False, allow_unicode=True)

            await self.send_message(f"```\n"
                                    f"{resp_yml}"
                                    f"```")

        except ClarificationRequired as e:
            await self.send_message(f"Clarification required: {[type(c).__name__ for c in e.required_clarifications]}")

        except InvalidRelativeDateException as e:
            await self.send_message(f"Invalid date: {e}")

        except Exception as e:
            log.exception("Exception during date parsing")
            await self.send_message(f"Unexpected error {type(e).__name__}: {e}")


class TgBot(TgBotBase):
    def _dispatch_initial_message(self, chat_obj) -> Optional[BotCommand]:

        msg = chat_obj.message["text"]  # type: str

        if msg == "/echo":
            return EchoCommand(self.app_wrapper.loop, chat_obj)
        elif msg == "/remind":
            return RemindCommand(self.app_wrapper.loop, chat_obj)
        elif msg == "/parse_date":
            return ParseDateCommand(self.app_wrapper.loop, chat_obj)

        # Trying to analyze phrase:
        tokens = tokenize_phrase(msg)

        token_fact_types = tuple(type(token.fact) for token in tokens)

        if token_fact_types in NaturalReminderCommand.REMINDER_PATTERNS:
            return NaturalReminderCommand(self.app_wrapper.loop, chat_obj, tokens)
