import re

import disnake
from disnake_plugins import Plugin

from src.bot import Bot

plugin = Plugin[Bot]()

CALCULATOR_REGEX = re.compile(r"^\(*\d+\.?\d*[0-9+\-*/.()^\s]+\d+\.?\d*\)+$")


@plugin.listener("on_message")
async def on_message(message: disnake.Message) -> None:
    if message.author.bot:
        return None
    if not CALCULATOR_REGEX.match(message.content):
        return None
    content = eval(message.content.replace("^", "**"))  # nosec # noqa: S307
    if message.content == str(content):
        return None
    await plugin.bot.reply(message, content)


setup, teardown = plugin.create_extension_handlers()
