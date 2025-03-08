from __future__ import annotations

import logging
import logging.handlers

from src import constants

__all__ = (
    "get_logger",
    "logger",
)


class LoggingFormatter(logging.Formatter):
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    reset = "\x1b[0m"
    bold = "\x1b[1m"
    colors = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record: logging.LogRecord, /) -> str:
        log_color = self.colors[record.levelno]
        fmt = (
            "(black){asctime}(reset)"
            " (levelcolor){levelname}(reset)"
            " (green){name}.{funcName}()(reset)"
            " {context}{message}"
        )
        fmt = fmt.replace("(black)", self.black + self.bold)
        fmt = fmt.replace("(reset)", self.reset)
        fmt = fmt.replace("(levelcolor)", log_color)
        fmt = fmt.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(fmt, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if hasattr(record, "context") and record.context:
            guild = f"{record.context.guild} ({record.context.guild.id})"
            channel = f"{record.context.channel} ({record.context.channel.id})"
            author = f"{record.context.author} ({record.context.author.id})"
            record.context = f"{guild} #{channel} @{author} "
        else:
            record.context = ""
        return True


formatter = LoggingFormatter()
author_filter = ContextFilter()

logger = logging.getLogger()
logger.setLevel(constants.Log.level)
logger.addFilter(author_filter)

stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(constants.Log.level)
stdout_handler.setFormatter(formatter)
stdout_handler.addFilter(author_filter)
logger.addHandler(stdout_handler)

logging.getLogger("disnake").setLevel(logging.WARNING)

logger.info("Logging has been initialized")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
