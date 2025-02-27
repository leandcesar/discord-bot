import disnake
from disnake.ext import commands
from disnake_plugins import Plugin

from src import log
from src.bot import Bot
from src.components import application_webhook

logger = log.get_logger(__name__)

plugin = Plugin[Bot]()


async def snipe_command(inter: commands.Context[commands.Bot] | disnake.GuildCommandInteraction) -> None:
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
    await snipe_command(ctx)


@plugin.slash_command(name="snipe")
async def snipe_slash_command(inter: disnake.GuildCommandInteraction) -> None:
    """
    Restore the last deleted message in the current channel.
    """
    await inter.response.defer(ephemeral=True)
    await snipe_command(inter)


@plugin.slash_command(name="fake")
async def fake_command(
    inter: disnake.GuildCommandInteraction,
    member: disnake.Member,
    content: str,
    attachment: disnake.Attachment | None = None,
) -> None:
    """
    Send a message impersonating another user in the current channel.

    Parameters
    ----------
    member: The guild member whose identity will be faked.
    content: The text content to be sent as if it were from the specified user.
    attachment: An optional media attachment to include with the message.
    """
    await inter.response.defer(ephemeral=True)
    webhook = await application_webhook(plugin.bot, inter.channel)
    options = {"username": member.display_name, "avatar_url": member.display_avatar.url, "wait": True}
    if attachment:
        options["file"] = await attachment.to_file()
    message = await webhook.send(content, **options)
    await inter.edit_original_response(message.jump_url)


@plugin.message_command(name="Undo edit")
async def undo_edit_command(inter: disnake.MessageCommandInteraction, message: disnake.Message) -> None:
    await inter.response.defer(ephemeral=True)
    if not message.edited_at:
        await inter.edit_original_response("💨")
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
