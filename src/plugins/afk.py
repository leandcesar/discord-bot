import datetime as dt
import json
import os

import disnake
from disnake.ext import commands
from disnake_plugins import Plugin

from src import constants, log
from src.bot import Bot

logger = log.get_logger(__name__)

plugin = Plugin[Bot]()


@plugin.load_hook()
async def afk_load_hook() -> None:
    os.makedirs(os.path.dirname(constants.AFK.path_filename), exist_ok=True)
    if os.path.exists(constants.AFK.path_filename):
        with open(constants.AFK.path_filename) as f:
            plugin.bot.afk_data = json.load(f)
    else:
        plugin.bot.afk_data = {}


async def persist_afk_data() -> None:
    with open(constants.AFK.path_filename, mode="w") as f:
        json.dump(plugin.bot.afk_data, f)


async def _afk_command(
    inter: commands.Context[commands.Bot] | disnake.GuildCommandInteraction,
) -> None:
    timestamp = int(dt.datetime.now(dt.timezone.utc).timestamp())
    plugin.bot.afk_data[str(inter.author.id)] = timestamp
    content = f"{constants.AFK.turn_on} (<t:{timestamp}:R>)"
    await persist_afk_data()

    if isinstance(inter, disnake.Interaction):
        await inter.edit_original_response(content)
    else:
        await inter.reply(content)


@plugin.command(name="afk")
async def afk_prefix_command(ctx: commands.Context[commands.Bot]) -> None:
    await _afk_command(ctx)


@plugin.slash_command(name="afk")
async def afk_slash_command(inter: disnake.GuildCommandInteraction) -> None:
    """
    Let others know you're AFK (Away From Keyboard).
    """
    await inter.response.defer()
    await _afk_command(inter)


@plugin.listener("on_message")
async def on_message(message: disnake.Message) -> None:
    if message.author.bot:
        return None

    for mention in message.mentions:
        if str(mention.id) in plugin.bot.afk_data:
            timestamp = int(plugin.bot.afk_data[str(mention.id)])
            content = f"{mention.mention} {constants.AFK.turn_on} (<t:{timestamp}:R>)"
            logger.info(
                f"{message.content!r} ({message.id}) -> {content!r}",
                extra={"context": message},
            )
            await message.reply(content, delete_after=10)

    # TODO: make condition dynamic in case the prefix or command name changes
    if message.content and message.content.startswith("+afk"):
        return None

    if str(message.author.id) in plugin.bot.afk_data:
        timestamp = int(plugin.bot.afk_data.pop(str(message.author.id)))
        content = f"{constants.AFK.turn_off} (<t:{timestamp}:R>)"
        await persist_afk_data()
        logger.info(
            f"{message.content!r} ({message.id}) -> {content!r}",
            extra={"context": message},
        )
        await message.reply(content)


setup, teardown = plugin.create_extension_handlers()
