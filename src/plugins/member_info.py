import disnake
from disnake.ext import commands
from disnake_plugins import Plugin

from src import log
from src.bot import Bot

logger = log.get_logger(__name__)

plugin = Plugin[Bot]()


@plugin.slash_command(name="member")
async def member_command(inter: disnake.GuildCommandInteraction) -> None:
    """
    ...  # TODO: add description
    """


async def avatar_command(
    inter: commands.Context[commands.Bot] | disnake.GuildCommandInteraction,
    *,
    member: disnake.Member,
) -> None:
    files = []
    file = await member.display_avatar.with_size(1024).to_file()
    files.append(file)
    if member.avatar and member.avatar != member.display_avatar:
        file = await member.avatar.with_size(1024).to_file()
        files.append(file)
    if isinstance(inter, disnake.Interaction):
        await inter.edit_original_response(files=files)
    else:
        await inter.reply(files=files)


@plugin.command(name="avatar")
async def avatar_prefix_command(
    ctx: commands.Context[commands.Bot],
    *,
    member: disnake.Member | None = None,
) -> None:
    if member is None:
        member = ctx.author
    await avatar_command(ctx, member=member)


@member_command.sub_command(name="avatar")
async def avatar_slash_command(
    inter: disnake.GuildCommandInteraction,
    member: disnake.Member = commands.Param(lambda inter: inter.author),
) -> None:
    """
    Display the specified member's avatar(s) in the highest available resolution.

    Parameters
    ----------
    member: The member whose avatar(s) will be retrieved and displayed.
    """
    await inter.response.defer()
    await avatar_command(inter, member=member)


async def banner_command(
    inter: commands.Context[commands.Bot] | disnake.GuildCommandInteraction,
    *,
    member: disnake.Member,
) -> None:
    files = []
    if member.banner:
        file = await member.banner.with_size(1024).to_file()
        files.append(file)
    if member.guild_banner and member.banner != member.guild_banner:
        file = await member.guild_banner.with_size(1024).to_file()
        files.append(file)
    if isinstance(inter, disnake.Interaction):
        await inter.edit_original_response(files=files)
    else:
        await inter.reply(files=files)


@plugin.command(name="banner")
async def banner_prefix_command(
    ctx: commands.Context[commands.Bot],
    *,
    member: disnake.Member | None = None,
) -> None:
    if member is None:
        member = ctx.author
    await banner_command(ctx, member=member)


@member_command.sub_command(name="banner")
async def banner_slash_command(
    inter: disnake.GuildCommandInteraction,
    member: disnake.Member = commands.Param(lambda inter: inter.author),
) -> None:
    """
    Display the specified member's banner(s) in the highest available resolution.

    Parameters
    ----------
    member: The member whose banner(s) will be retrieved and displayed.
    """
    await inter.response.defer()
    await banner_command(inter, member=member)


setup, teardown = plugin.create_extension_handlers()
