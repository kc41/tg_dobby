import asyncio
from aiohttp import web
import aioredis

from tg_notificator.tg_bot_base import TgBotBase
from tg_notificator.settings import AppSettings
from tg_notificator.user_registry import AbstractUserRegistry


# TODO CONSIDER: use as web.Application mixin (check options for typing)
class AppWrapper:
    KEY_BOT = "bot"
    KEY_BOT_TASK = "bot_task"
    KEY_REDIS = "redis"
    KEY_USER_REGISTRY = "user_registry"
    KEY_SETTINGS = "settings"

    __slots__ = ("_app",)

    def __init__(self, app: web.Application):
        self._app = app

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._app.loop

    @property
    def bot(self) -> TgBotBase:
        return self._app[self.KEY_BOT]

    @bot.setter
    def bot(self, val: TgBotBase):
        self._app[self.KEY_BOT] = val

    @property
    def bot_task(self) -> asyncio.Task:
        return self._app[self.KEY_BOT_TASK]

    @bot_task.setter
    def bot_task(self, val: asyncio.Task):
        self._app[self.KEY_BOT_TASK] = val

    @property
    def redis(self) -> aioredis.Redis:
        return self._app[self.KEY_REDIS]

    @redis.setter
    def redis(self, val: aioredis.Redis):
        self._app[self.KEY_REDIS] = val

    @property
    def user_registry(self) -> AbstractUserRegistry:
        return self._app[self.KEY_USER_REGISTRY]

    @user_registry.setter
    def user_registry(self, val: AbstractUserRegistry):
        self._app[self.KEY_USER_REGISTRY] = val

    @property
    def settings(self) -> AppSettings:
        return self._app[self.KEY_SETTINGS]

    @settings.setter
    def settings(self, value: AppSettings):
        self._app[self.KEY_SETTINGS] = value
