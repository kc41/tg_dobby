from abc import ABC, abstractmethod

from typing import TYPE_CHECKING, Optional, List
import pydantic

if TYPE_CHECKING:
    from aioredis import Redis


class TgUser(pydantic.BaseModel):
    username: str
    private_chat_id: str


class AbstractUserRegistry(ABC):

    @abstractmethod
    async def save_user(self, user: TgUser):
        pass

    @abstractmethod
    async def get_user_by_username(self, username: str) -> TgUser:
        pass

    @abstractmethod
    async def list_users(self) -> List[TgUser]:
        pass


class RedisHashSetUserRegistry(AbstractUserRegistry):
    def __init__(self, redis: "Redis"):
        self._redis = redis

    async def save_user(self, user: TgUser):
        await self._redis.hmset_dict(f"tguser:{user.username}:info", user.dict())

    async def get_user_by_username(self, username: str) -> Optional[TgUser]:
        user_dict = await self._redis.hgetall(f"tguser:{username}:info", encoding="utf-8")

        if not user_dict:
            return None

        return TgUser(**user_dict)

    async def list_users(self) -> List[TgUser]:
        users_keys = await self._redis.keys("tguser:*:info")

        return [
            TgUser(**(await self._redis.hgetall(key, encoding="utf-8")))
            for key in users_keys
        ]
