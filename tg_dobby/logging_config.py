import logging
import logging.config

LOG_FMT = '[%(asctime)s] %(name)-30s %(levelname)-8s %(message)s'


def init_logging():
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'class': 'logging.Formatter',
                'format': LOG_FMT
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'default'
            },
        },
        'loggers': {
            '': {
                'handlers': ['console'],
                'level': 'INFO',
            },

            'aiohttp.access': {
                'level': 'INFO',
            },
            'aiohttp.server': {
                'level': 'INFO',
            },

            '__main__': {
                'level': 'INFO',
            },

            'tg_dobby.app': {
                'level': 'INFO',
            },

            'aiotg': {
                'level': 'DEBUG',
            },
        },
    })
