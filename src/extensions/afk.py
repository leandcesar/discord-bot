import datetime as dt

import disnake
from disnake.ext import commands
from disnake_plugins import Plugin

from src import config
from src.bot import Bot as _Bot
from src.util.persistent_dict import PersistentDict


class Bot(_Bot):
    afk_data: PersistentDict


plugin = Plugin[Bot]()


@plugin.load_hook()
async def afk_load_hook() -> None:
    plugin.bot.afk_data = PersistentDict.from_file(config.File.afk)


async def _afk_command(inter: commands.Context[Bot] | disnake.ApplicationCommandInteraction) -> None:
    timestamp = int(dt.datetime.now(dt.timezone.utc).timestamp())
    plugin.bot.afk_data[inter.author.id] = timestamp
    await plugin.bot.reply(inter, f"{config.Emoji.afk_turn_on} (<t:{timestamp}:R>)")


@plugin.command(name="afk", description="Let others know you're AFK (Away From Keyboard).")
async def afk_prefix_command(ctx: commands.Context[Bot]) -> None:
    await _afk_command(ctx)


@plugin.slash_command(name="afk")
async def afk_slash_command(inter: disnake.ApplicationCommandInteraction) -> None:
    """
    Let others know you're AFK (Away From Keyboard).
    """
    await _afk_command(inter)


@plugin.listener("on_message")
async def on_message(message: disnake.Message) -> None:
    if message.author.bot:
        return None
    for mention in message.mentions:
        if mention.id in plugin.bot.afk_data:
            timestamp = plugin.bot.afk_data[mention.id]
            await plugin.bot.reply(
                message, f"{mention.mention} {config.Emoji.afk_turn_on} (<t:{timestamp}:R>)", delete_after=10
            )
    prefix = await plugin.bot.get_prefix(message)
    if isinstance(prefix, list):
        if any(message.content.startswith(f"{p}afk") for p in prefix):
            return None
    elif message.content.startswith(f"{prefix}afk"):
        return None
    if message.author.id in plugin.bot.afk_data:
        timestamp = plugin.bot.afk_data.pop(message.author.id)
        await plugin.bot.reply(message, f"{config.Emoji.afk_turn_off} (<t:{timestamp}:R>)", mention_author=False)


setup, teardown = plugin.create_extension_handlers()
