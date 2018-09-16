from abc import ABC, abstractmethod, ABCMeta
from typing import TYPE_CHECKING, Dict, Optional

import logging

from aiotg import Bot, Chat, asyncio

from tg_notificator.user_registry import TgUser

if TYPE_CHECKING:
    from tg_notificator.appw import AppWrapper

log = logging.getLogger(__name__)


# TODO CONSIDER: save initial message in constructor
class BotCommand(ABC):

    def __init__(self, loop: asyncio.AbstractEventLoop):
        self._q = asyncio.Queue(loop=loop)

    @abstractmethod
    async def run(self, initial_message: Chat):
        pass

    async def next_message(self) -> Chat:
        log.info(f"Awaiting next message")
        msg = await self._q.get()
        log.info(f"Message received {msg}")
        return msg


# TODO FIX: implement own Telegram API wrapper
class TgBotBase(Bot, metaclass=ABCMeta):
    def __init__(self, api_token, app_wrapper: "AppWrapper", *args, **kwargs):
        super().__init__(api_token=api_token, *args, **kwargs)
        self.app_wrapper = app_wrapper
        self.add_command(r".*", self.handle_inbound_message)

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
                # noinspection PyProtectedMember
                running_command._q.put_nowait(chat_obj)

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
