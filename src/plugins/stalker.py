import disnake
from disnake.ext import commands
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


@plugin.listener("on_message_edit")
async def on_message_edit(before: disnake.Message, after: disnake.Message) -> None:
    if before.author.bot:
        return None
    logger.debug(
        f"{before.content!r} ({before.id}) -> {after.content!r}",
        extra={"context": before},
    )
    plugin.bot.edited_messages.append(before)


@plugin.listener("on_message_delete")
async def on_message_delete(message: disnake.Message) -> None:
    if message.author.bot:
        return None
    logger.info(
        f"{message.content!r} ({message.id}) ",
        extra={"context": message},
    )
    plugin.bot.deleted_messages.append(message)


@plugin.listener("on_bulk_message_delete")
async def on_bulk_message_delete(messages: list[disnake.Message]) -> None:
    for message in messages:
        await on_message_delete(message)


async def _snipe_command(inter: commands.Context[commands.Bot] | disnake.GuildCommandInteraction) -> None:
    for m in plugin.bot.deleted_messages[::-1]:
        if m.channel.id == inter.channel.id:
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
                await inter.edit_original_response(webhook_message.jump_url)
            break
    else:
        if isinstance(inter, disnake.Interaction):
            await inter.edit_original_response("💨")


@plugin.command(name="snipe")
async def snipe_prefix_command(ctx: commands.Context[commands.Bot]) -> None:
    await _snipe_command(ctx)


@plugin.slash_command(name="snipe")
async def snipe_slash_command(inter: disnake.GuildCommandInteraction) -> None:
    """
    Restore the last deleted message in the current channel.
    """
    await inter.response.defer(ephemeral=True)
    await _snipe_command(inter)


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
            await inter.edit_original_response(webhook_message.jump_url)
            break
    else:
        await inter.edit_original_response("💨")


setup, teardown = plugin.create_extension_handlers()
