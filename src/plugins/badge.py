import disnake
from disnake.ext import commands
from disnake_plugins import Plugin

from src import log
from src.bot import Bot

logger = log.get_logger(__name__)

plugin = Plugin[Bot]()


def member_has_badge_role(inter: disnake.GuildCommandInteraction) -> bool:
    return inter.author.top_role != inter.guild.default_role


def guild_has_role_icons(inter: disnake.GuildCommandInteraction) -> bool:
    return "ROLE_ICONS" in inter.guild.features


@commands.check(member_has_badge_role)
@commands.check(guild_has_role_icons)
@plugin.slash_command(name="badge")
async def badge_command(
    inter: disnake.GuildCommandInteraction,
    emote: disnake.PartialEmoji | None = None,
    attachment: disnake.Attachment | None = None,
) -> None:
    """
    Change your badge on the server.

    Parameters
    ----------
    emote: The emote or emoji to set as your badge.
    attachment: An image file to use as the badge.
    """
    await inter.response.defer(ephemeral=True)
    if emote and emote.is_unicode_emoji():
        role = await inter.author.top_role.edit(icon=None, emoji=emote)
    elif emote and emote.is_custom_emoji():
        role = await inter.author.top_role.edit(icon=emote, emoji=None)
    elif attachment:
        emote = await attachment.read()
        role = await inter.author.top_role.edit(icon=emote, emoji=None)
    else:
        role = inter.author.top_role

    badge = role.icon if role.icon else role.emoji if role.emoji else None
    if badge:
        file = await badge.to_file()
        await inter.edit_original_response(file=file)


setup, teardown = plugin.create_extension_handlers()
