'''Module responsible for application logging'''
from logging.config import dictConfig
import logging
import os

LOG_PATH = 'log/'
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

dictConfig({
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)-4s %(funcName)s() L%(lineno)-4d %(message)s",
        },
        "detailed": {
            "format": "[%(asctime)s] %(levelname)-4s %(funcName)s() L%(lineno)-4d %(message)s - call_trace=%(pathname)s L%(lineno)-4d",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        # "email": {
        #     "class": "logging.handlers.SMTPHandler",
        #     "formatter": "default",
        #     "level": "ERROR",
        #     "mailhost": ("smtp.example.com", 587),
        #     "fromaddr": "devops@example.com",
        #     "toaddrs": ["receiver@example.com", "receiver2@example.com"],
        #     "subject": "Error Logs",
        #     "credentials": ("username", "password"),
        # },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "filename": "log/error.log",
            "maxBytes": 100000,
            "backupCount": 10,
            "delay": "False",
        },
        "detailed_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "filename": "log/detailed.log",
            "maxBytes": 100000,
            "backupCount": 5,
            "delay": "False",
        }
    },
    "loggers": {
        "gunicorn.error": {
            "handlers": ["console", "error_file"],  #, email],
            "level": "DEBUG",
            "propagate": False,
        }
    },
    "root": {
        "handlers": ["console", "detailed_file"],
        "level": "DEBUG",
    }
})

logger = logging.getLogger(__name__)
