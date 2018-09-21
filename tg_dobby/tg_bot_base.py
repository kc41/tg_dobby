from abc import ABC, abstractmethod, ABCMeta
from typing import TYPE_CHECKING, Dict, Optional, Union, List, Set

import logging

from aiotg import Bot, Chat, asyncio
import aiotg

import pydantic

from tg_dobby.user_registry import TgUser

if TYPE_CHECKING:
    from tg_dobby.appw import AppWrapper

log = logging.getLogger(__name__)


class TgModel(pydantic.BaseModel):
    class Config:
        TG_TYPE = None

    def dict(self, *, include: Set[str] = None, exclude: Set[str] = set(), by_alias: bool = False):
        ret = super().dict(include=include, exclude=exclude, by_alias=by_alias)
        ret.update({"type": self.Config.TG_TYPE})

        return ret


class InlineKeyboardButtonData(TgModel):
    class Config:
        TG_TYPE = "InlineKeyboardButton"

    text: str
    callback_data: Optional[str] = None


class InlineKeyboardMarkupData(TgModel):
    class Config:
        TG_TYPE = "InlineKeyboardMarkup"

    inline_keyboard: List[List[InlineKeyboardButtonData]]


class MessageData(TgModel):
    class Config:
        TG_TYPE = "Message"

    message_id: int
    text: Optional[str] = None


class CallbackQueryData(pydantic.BaseModel):
    class Config:
        TG_TYPE = "CallbackQuery"

    id: str
    message: MessageData
    data: Optional[str]


class BotCommand(ABC):

    def __init__(self, loop: asyncio.AbstractEventLoop, initial_chat_obj: Chat):
        self._q = asyncio.Queue(loop=loop)

        self.bot = initial_chat_obj.bot  # type: Bot
        self.chat_id = initial_chat_obj.id

    async def edit_message_reply_markup(self, message: Union[MessageData, int], markup: InlineKeyboardMarkupData):
        message_id = message if isinstance(message, int) else message.message_id

        args = {
            "message_id": message_id,
            "chat_id": self.chat_id,
        }

        if markup:
            args["reply_markup"] = markup.json()

        return await self.bot.api_call("editMessageReplyMarkup", **args)

    async def send_message(self, text, parse_mode="Markdown", reply_markup: InlineKeyboardMarkupData = None):
        args = {
            "text": text,
            "chat_id": self.chat_id,
            "parse_mode": parse_mode,
        }

        if reply_markup:
            args["reply_markup"] = reply_markup.json()

        return await self.bot.api_call("sendMessage", **args)

    async def answer_callback_query(self, callback_query: Union[CallbackQueryData, str]):
        callback_query_id = callback_query if isinstance(callback_query, str) else callback_query.id

        return await self.bot.api_call("answerCallbackQuery", callback_query_id=callback_query_id)

    @abstractmethod
    async def run(self, initial_message: Chat):
        pass

    async def next_update(self) -> Union[MessageData, CallbackQueryData]:
        log.info(f"Awaiting next message")
        msg = await self._q.get()
        log.info(f"Message received {msg}")
        return msg

    async def next_message(self) -> MessageData:
        while True:
            next_data = await self.next_update()
            if isinstance(next_data, MessageData):
                return next_data

    async def next_callback(self) -> CallbackQueryData:
        while True:
            next_data = await self.next_update()
            if isinstance(next_data, CallbackQueryData):
                return next_data


class TgBotBase(Bot, metaclass=ABCMeta):
    def __init__(self, api_token, app_wrapper: "AppWrapper", *args, **kwargs):
        super().__init__(api_token=api_token, *args, **kwargs)
        self.app_wrapper = app_wrapper

        self.add_command(r".*", self.handle_inbound_message)
        self.add_callback(r".*", self.handle_inbound_message)

        self.map_chat_id_running_command = {}  # type: Dict[str, BotCommand]

    @staticmethod
    def tg_user_from_chat_obj(chat_obj: Chat):
        return TgUser(
            username=chat_obj.sender["username"],
            private_chat_id=chat_obj.id
        )

    async def _pre_process_msg(self, chat_obj: Chat):
        # Storing private chat ID and updating other user data
        if chat_obj.type == "private":
            username = chat_obj.sender["username"]

            new_user = self.tg_user_from_chat_obj(chat_obj)
            existing_user = await self.app_wrapper.user_registry.get_user_by_username(username)

            if new_user != existing_user:
                await self.app_wrapper.user_registry.save_user(new_user)

    # TODO CONSIDER: restrict time of command execution
    async def _run_command(self, command: BotCommand, chat: Chat):
        self.map_chat_id_running_command[chat.id] = command

        # noinspection PyBroadException
        try:
            log.info(f"Running command '{type(command).__name__}'")
            await command.run(chat)
        except Exception:
            log.exception(f"Exception during executing '{type(command).__name__}' command {repr(command)}")

        log.info(f"Command '{type(command).__name__}' was finished. Removing from registry...")
        self.map_chat_id_running_command.pop(chat.id)

    @abstractmethod
    def _dispatch_initial_message(self, chat_obj) -> Optional[BotCommand]:
        """
        Implementation should determine which command to run.
        If None was returned, user will be informed that command is unknown
        :param chat_obj: aiotg.Chat object for initial message
        :return: BotCommand to run
        """

    async def handle_inbound_message(self, chat_obj: Chat, *args, **kwargs):
        # noinspection PyBroadException
        try:
            log.debug(f"Handling inbound message {chat_obj}. args={args} kwargs={kwargs}")
            await self._pre_process_msg(chat_obj)

            running_command = self.map_chat_id_running_command.get(chat_obj.id)

            if running_command:
                if len(args) > 0 and isinstance(args[0], aiotg.CallbackQuery):
                    data = CallbackQueryData(**args[0].src)
                else:
                    data = MessageData(**chat_obj.message)

                # noinspection PyProtectedMember
                running_command._q.put_nowait(data)

            else:
                new_command = self._dispatch_initial_message(chat_obj)

                if new_command:
                    log.info(f"Command '{type(new_command).__name__}' was created")

                    # TODO FIX: save task reference to close correctly on exit
                    asyncio.ensure_future(self._run_command(new_command, chat_obj))

                else:
                    chat_obj.reply("Unknown command!")

        except Exception:
            log.exception(f"Exception during handling inbound message {chat_obj}")
