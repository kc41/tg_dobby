import logging

import asyncio

import aioredis
from aiohttp import web

from tg_dobby import views
from tg_dobby.appw import AppWrapper
from tg_dobby.tg_bot import TgBot
from tg_dobby.settings import AppSettings
from tg_dobby.user_registry import RedisHashSetUserRegistry

log = logging.getLogger(__name__)


async def on_shutdown(app: web.Application):
    app_wrapper = AppWrapper(app)

    log.info("Canceling bot task")
    app_wrapper.bot_task.cancel()
    app_wrapper.bot.stop()
    await app_wrapper.bot.session.close()

    log.info("Closing Redis pool")
    app_wrapper.redis.close()

    log.info("On shutdown procedure finished")


async def on_startup(app: web.Application):
    log.info("Running startup procedure")

    app_wrapper = AppWrapper(app)

    log.info("Creating Redis pool")
    redis = await aioredis.create_redis(app_wrapper.settings.redis_url)

    app_wrapper.redis = redis
    app_wrapper.user_registry = RedisHashSetUserRegistry(redis=redis)

    log.info("Creating bot task")
    app_wrapper.bot_task = asyncio.ensure_future(
        app_wrapper.bot.loop(),
        loop=app.loop
    )

    log.info("Startup procedure finished")


def create_application(settings: AppSettings):
    log.info("Creating application")

    app = web.Application()
    app_wrapper = AppWrapper(app)
    app_wrapper.settings = settings

    app_wrapper.bot = TgBot(api_token=settings.bot_api_key, app_wrapper=app_wrapper)

    app_wrapper.redis = None
    app_wrapper.user_registry = None

    app.add_routes([
        web.view("/notify/", views.NotifyView),
        web.view("/users/", views.ListUserView),
    ])

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    return app
