import re

import disnake
from disnake_plugins import Plugin

from src import log
from src.bot import Bot

logger = log.get_logger(__name__)

plugin = Plugin[Bot]()

PATTERN = r"^\(*\d+\.?\d*[0-9+\-*/.()^\s]+\d+\.?\d*\)*$"
REGEX = re.compile(PATTERN)


@plugin.listener("on_message")
async def on_message(message: disnake.Message) -> None:
    if message.author.bot:
        return None
    if not REGEX.match(message.content):
        return None
    try:
        result = eval(message.content.replace("^", "**"))  # nosec # noqa: S307
    except Exception as e:
        logger.error(
            f"{message.content!r} ({message.id}) {e}",
            extra={"context": message},
        )
        return None
    if message.content == str(result):
        return None
    logger.debug(
        f"{message.content!r} ({message.id}) = {result!r}",
        extra={"context": message},
    )
    await message.reply(result)


setup, teardown = plugin.create_extension_handlers()
