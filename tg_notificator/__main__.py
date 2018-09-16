import logging
import asyncio

import sys
from aiohttp import web

from tg_notificator.app import create_application
from tg_notificator.logging_config import init_logging
from tg_notificator.settings import AppSettings

log = logging.getLogger(__name__)


async def init_app(settings: AppSettings) -> web.AppRunner:
    app = create_application(settings)

    runner = web.AppRunner(app)

    try:
        await runner.setup()

        site = web.TCPSite(runner, settings.http_bind_address, settings.http_bind_port)
        await site.start()

        return runner

    except Exception as e:
        log.error("Exception during app start-up. Shutting application down...")
        await app.shutdown()
        raise e


def main():
    settings = AppSettings()

    init_logging()

    log.info(f"Running TG notificator server at {settings.http_bind_address}:{settings.http_bind_port}.")

    log.info(f"Preparing HTTP server")

    loop = asyncio.get_event_loop()

    try:
        runner = loop.run_until_complete(init_app(settings))
    except KeyboardInterrupt:
        log.info("Interrupt signal received during initialization")
        loop.close()
        sys.exit(-1)
    except Exception as e:
        log.exception(e)
        loop.close()
        sys.exit(-1)

    try:
        log.info(f"Running main event loop forever")
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        log.info("Interrupt signal received")
        loop.run_until_complete(runner.cleanup())
        loop.close()


if __name__ == '__main__':
    main()
