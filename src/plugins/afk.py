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

AFK_TURN_ON = "🔕"
AFK_TURN_OFF = "🔔"
AFK_PATH_FILE = os.path.join(constants.AFK.path, constants.AFK.filename)


@plugin.load_hook()
async def load_afk_data() -> None:
    folder = os.path.dirname(AFK_PATH_FILE)
    if not os.path.exists(folder):
        os.makedirs(folder)
    if not os.path.exists(AFK_PATH_FILE):
        with open(AFK_PATH_FILE, mode="w") as f:
            f.write(json.dumps({}, indent=4))
    with open(AFK_PATH_FILE) as f:
        plugin.bot.afk_data = json.loads(f.read())


@plugin.unload_hook()
async def persist_afk_data() -> None:
    with open(AFK_PATH_FILE, mode="w") as f:
        f.write(json.dumps(plugin.bot.afk_data, indent=4))


@plugin.listener("on_message")
async def on_message(message: disnake.Message) -> None:
    if message.author.bot:
        return None
    for mention in message.mentions:
        if str(mention.id) in plugin.bot.afk_data:
            datetime_isoformat = plugin.bot.afk_data[str(mention.id)]
            datetime = dt.datetime.fromisoformat(datetime_isoformat)
            content = f"{mention.mention} {AFK_TURN_ON} (<t:{int(datetime.timestamp())}:R>)"
            logger.debug(
                f"{message.guild} ({message.guild.id}) "
                f"#{message.channel} ({message.channel.id}) "
                f"@{message.author} ({message.author.id}): "
                f"{message.content!r} ({message.id}) "
                f"-> {content!r}"
            )
            await message.reply(content, delete_after=10)
    # TODO: make condition dynamic in case the prefix or command name changes
    if message.content and message.content.startswith("+afk"):
        return None
    if str(message.author.id) in plugin.bot.afk_data:
        datetime_isoformat = plugin.bot.afk_data.pop(str(message.author.id))
        await persist_afk_data()
        datetime = dt.datetime.fromisoformat(datetime_isoformat)
        content = f"{AFK_TURN_OFF} (<t:{int(datetime.timestamp())}:R>)"
        logger.debug(
            f"{message.guild} ({message.guild.id}) "
            f"#{message.channel} ({message.channel.id}) "
            f"@{message.author} ({message.author.id}): "
            f"{message.content!r} ({message.id}) "
            f"-> {content!r}"
        )
        await message.reply(content)


async def afk_command(
    inter: commands.Context[commands.Bot] | disnake.GuildCommandInteraction,
) -> None:
    datetime = dt.datetime.utcnow()
    plugin.bot.afk_data[str(inter.author.id)] = datetime.isoformat()
    await persist_afk_data()
    content = f"{AFK_TURN_ON} (<t:{int(datetime.timestamp())}:R>)"
    if isinstance(inter, disnake.Interaction):
        await inter.edit_original_response(content)
    else:
        await inter.reply(content, mention_author=False)


@plugin.command(name="afk")
async def afk_prefix_command(ctx: commands.Context[commands.Bot]) -> None:
    await afk_command(ctx)


@plugin.slash_command(name="afk")
async def afk_slash_command(inter: disnake.GuildCommandInteraction) -> None:
    """
    Let others know you're AFK (Away From Keyboard).
    """
    await inter.response.defer()
    await afk_command(inter)


setup, teardown = plugin.create_extension_handlers()
