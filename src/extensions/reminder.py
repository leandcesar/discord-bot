import datetime as dt

import disnake
from disnake.ext import commands, tasks
from disnake.ext.commands.errors import MissingRequiredArgument
from disnake_plugins import Plugin

from src import config
from src.api.witai import WitAI
from src.bot import Bot as _Bot
from src.util.persistent_dict import PersistentDict


class Bot(_Bot):
    wit_ai: WitAI
    reminder_data: PersistentDict


plugin = Plugin[Bot]()


@plugin.load_hook()
async def reminder_load_hook() -> None:
    plugin.bot.wit_ai = WitAI(config.WitAI.access_token)
    plugin.bot.reminder_data = PersistentDict.from_file(config.File.reminder)
    reminder.start()


@plugin.unload_hook()
async def reminder_unload_hook() -> None:
    await plugin.bot.wit_ai.close()


async def _remind_command(
    inter: commands.Context[Bot] | disnake.ApplicationCommandInteraction,
    *,
    content: str,
) -> None:
    datetime = await plugin.bot.wit_ai.detect_datetime(content)
    if not datetime:
        raise MissingRequiredArgument("Could not detect a valid date and time in the provided content.")
    scheduled_to = int(datetime.timestamp())
    created_at = int(dt.datetime.now(dt.timezone.utc).timestamp())
    plugin.bot.reminder_data[scheduled_to] = {
        "guild_id": inter.guild.id,
        "channel_id": inter.channel.id,
        "member_id": inter.author.id,
        "message_id": inter.message.id if hasattr(inter, "message") else None,
        "content": content,
        "created_at": created_at,
        "scheduled_to": scheduled_to,
    }
    await plugin.bot.reply(inter, f"{config.Emoji.remind_created} <t:{scheduled_to}:R>")


@plugin.command(name="remind", aliases=["remindme"], description="Set a reminder for yourself or others.")
async def remind_prefix_command(
    ctx: commands.Context[Bot],
    *,
    content: str,
) -> None:
    await _remind_command(ctx, content=content)


@plugin.slash_command(name="remind")
async def remind_slash_command(
    inter: disnake.ApplicationCommandInteraction,
    content: str,
) -> None:
    """
    Set a reminder for yourself or others.

    Parameters
    ----------
    content: The reminder message, and the date and time when the reminder should be triggered.
    """
    await inter.response.defer()
    await _remind_command(inter, content=content)


@tasks.loop(seconds=10)
async def reminder() -> None:
    reminder_data = sorted(plugin.bot.reminder_data.copy().items())
    timestamp = int(dt.datetime.now(dt.timezone.utc).timestamp())
    for key, remind in reminder_data:
        if timestamp > remind["scheduled_to"]:
            content = remind["content"]
            timestamp = remind["created_at"]
            guild = await plugin.bot.fetch_guild(remind["guild_id"])
            channel = await guild.fetch_channel(remind["channel_id"])
            author = await guild.fetch_member(remind["member_id"])
            if remind["message_id"]:
                original_message = await channel.fetch_message(int(remind["message_id"]))
                message = await plugin.bot.reply(
                    original_message,
                    f"{config.Emoji.remind_delivered} {author.mention}: {content} (<t:{timestamp}:R>)",
                )
            else:
                message = await plugin.bot.reply(
                    channel, f"{config.Emoji.remind_delivered} {author.mention}: {content} (<t:{timestamp}:R>)"
                )
            plugin.bot.reminder_data.pop(key, None)
            await author.create_dm()
            await message.forward(author.dm_channel)
        else:
            break


setup, teardown = plugin.create_extension_handlers()
