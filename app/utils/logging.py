import logging
import re

from rich.console import Console
from rich.logging import RichHandler


from app.utils.singleton import SingletonMeta
from logging.config import dictConfig


class AppLogger(metaclass=SingletonMeta):
    _logger = None

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def get_logger(self):
        return self._logger


class RichConsoleHandler(RichHandler):
    def __init__(self, width=300, style=None, **kwargs):
        super().__init__(
            show_level=False,
            show_time=False,
            console=Console(color_system="256", width=width, style=style),
            **kwargs
        )


class CustomFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        arg_pattern = re.compile(r"%\((\w+)\)")
        arg_names = [x.group(1) for x in arg_pattern.finditer(self._fmt)]
        for field in arg_names:
            if field not in record.__dict__:
                record.__dict__[field] = None

        return super().format(record)


def _configure_logging():
    # debug_handler = RotatingFileHandler(
    #     "/app/logs/debug.log", maxBytes=25 * 1024 * 1024, backupCount=5
    # )
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "class": "app.utils.logging.CustomFormatter",
                # "datefmt": "%d/%m/%Y %H:%M:%S",
                "format": "%(levelname)-10s %(asctime)s|%(module)s:%(lineno)s|%(funcName)s|[MSG] %(message)s",
            },
            "fileFormatter": {
                "class": "app.utils.logging.CustomFormatter",
                # "datefmt": "%d/%m/%Y %H:%M:%S",
                "format": "%(levelname)-10s%(asctime)s|%(module)s:%(lineno)s|%(funcName)s|[MSG] %(message)s",
            },
            "consoleFormatter": {
                "class": "app.utils.logging.CustomFormatter",
                # "datefmt": "%d/%m/%Y %H:%M:%S",
                "format": "%(levelname)-10s%(asctime)s|%(module)s:%(lineno)s|%(funcName)s|[MSG] %(message)s",
            },
        },
        "filters": {
            "correlation_id": {
                "()": "asgi_correlation_id.CorrelationIdFilter",
                "uuid_length": 8,
                "default_value": "-",
            },
        },
        "handlers": {
            "stream_info": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "INFO",
            },
            "consoleHandler": {
                "class": "logging.StreamHandler",
                "filters": ["correlation_id"],
                "formatter": "consoleFormatter",
                "level": "INFO",
            },
            "debug_fileHandler": {
                "class": "logging.handlers.RotatingFileHandler",
                "filters": ["correlation_id"],
                "formatter": "fileFormatter",
                "level": "DEBUG",
                "filename": "/debug.log",
                "mode": "a",
                "maxBytes": 25 * 1024 * 1024,
                "backupCount": 5,
            },
            "error_fileHandler": {
                "class": "logging.handlers.RotatingFileHandler",
                "filters": ["correlation_id"],
                "formatter": "fileFormatter",
                "level": "ERROR",
                "filename": "/error.log",
                "mode": "a",
                "maxBytes": 25 * 1024 * 1024,
                "backupCount": 5,
            },
        },
        "loggers": {
            "root": {
                "handlers": ["stream_info"],
                "level": "INFO",
                "propagate": False,
            },
            "full_info": {
                "handlers": [
                    "consoleHandler",
                    "debug_fileHandler",
                    "error_fileHandler",
                ],
                "level": "DEBUG",
                "propagate": False,
                "qualname": "full_info",
            },
            "uvicorn.access": {
                "handlers": ["consoleHandler", "debug_fileHandler"],
                "level": "DEBUG",
                "propagate": False,
                "qualname": "uvicorn.access",
            },
            "uvicorn.error": {
                "handlers": [
                    "consoleHandler",
                    "debug_fileHandler",
                    "error_fileHandler",
                ],
                "level": "ERROR",
                "propagate": False,
                "qualname": "uvicorn.error",
            },
        },
    }
    dictConfig(LOGGING)