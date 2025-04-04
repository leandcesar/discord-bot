import disnake
from disnake_plugins import Plugin

from src.bot import Bot
from src.util.webhook import application_webhook

plugin = Plugin[Bot]()


@plugin.slash_command(name="fake")
async def fake_command(
    inter: disnake.ApplicationCommandInteraction,
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
    files = [await attachment.to_file()] if attachment else []
    webhook_message = await webhook.send(
        content,
        username=member.display_name,
        avatar_url=member.display_avatar.url,
        files=files,
        wait=True,
    )
    await plugin.bot.reply(inter, webhook_message.jump_url)


setup, teardown = plugin.create_extension_handlers()
