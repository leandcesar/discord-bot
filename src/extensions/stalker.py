import disnake
from disnake.ext import commands
from disnake.ext.commands.errors import BadArgument, CommandError
from disnake_plugins import Plugin

from src import log
from src.bot import Bot
from src.util.webhook import application_webhook

logger = log.get_logger(__name__)
plugin = Plugin[Bot]()


@plugin.load_hook()
async def stalker_load_hook() -> None:
    plugin.bot.deleted_messages = []
    plugin.bot.edited_messages = []


@plugin.listener("on_message")
async def on_message(message: disnake.Message) -> None:
    logger.debug(f"{message.content!r} ({message.id})", extra={"inter": message})


@plugin.listener("on_message_edit")
async def on_message_edit(before: disnake.Message, after: disnake.Message) -> None:
    if before.author.bot:
        return None
    logger.debug(f"{before.content!r} ({before.id}) = {after.content!r}", extra={"inter": before})
    plugin.bot.edited_messages.append(before)


@plugin.listener("on_message_delete")
async def on_message_delete(message: disnake.Message) -> None:
    if message.author.bot:
        return None
    logger.info(f"{message.content!r} ({message.id})", extra={"inter": message})
    plugin.bot.deleted_messages.append(message)


@plugin.listener("on_bulk_message_delete")
async def on_bulk_message_delete(messages: list[disnake.Message]) -> None:
    for message in messages:
        await on_message_delete(message)


async def _snipe_command(
    inter: commands.Context[Bot] | disnake.ApplicationCommandInteraction, offset: int = 1
) -> None:
    index = 0
    for m in plugin.bot.deleted_messages[::-1]:
        if m.channel.id == inter.channel.id:
            index += 1
            if index < offset:
                continue
            member = await inter.guild.fetch_member(m.author.id)
            webhook = await application_webhook(plugin.bot, m.channel)
            files = [await attachment.to_file() for attachment in m.attachments]
            webhook_message = await webhook.send(
                m.content,
                username=member.display_name,
                avatar_url=member.display_avatar.url,
                files=files,
                wait=True,
            )
            if isinstance(inter, disnake.Interaction):
                await plugin.bot.reply(inter, webhook_message.jump_url)
            break
    else:
        raise CommandError("Make sure at least one message has been deleted.")


@plugin.command(name="snipe", description="Restore the last deleted message in the current channel.")
async def snipe_prefix_command(ctx: commands.Context[Bot], offset: int = 1) -> None:
    await _snipe_command(ctx, offset=offset)


@plugin.slash_command(name="snipe")
async def snipe_slash_command(inter: disnake.ApplicationCommandInteraction, offset: int = 1) -> None:
    """
    Restore the last deleted message in the current channel.

    Parameters
    ----------
    offset: The position of the deleted message to restore, with 1 being the most recent.
    """
    await inter.response.defer(ephemeral=True)
    await _snipe_command(inter, offset=offset)


@plugin.message_command(name="Undo edit")
async def undo_message_command(inter: disnake.MessageCommandInteraction, message: disnake.Message) -> None:
    await inter.response.defer(ephemeral=True)
    for m in plugin.bot.edited_messages[::-1]:
        if m.id == message.id:
            member = await inter.guild.fetch_member(m.author.id)
            webhook = await application_webhook(plugin.bot, m.channel)
            files = [await attachment.to_file() for attachment in m.attachments]
            webhook_message = await webhook.send(
                m.content,
                username=member.display_name,
                avatar_url=member.display_avatar.url,
                files=files,
                wait=True,
            )
            await plugin.bot.reply(inter, webhook_message.jump_url)
            break
    else:
        raise BadArgument("Make sure the message was edited.")


setup, teardown = plugin.create_extension_handlers()
