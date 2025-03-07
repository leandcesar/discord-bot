import disnake
from disnake.ext import commands
from disnake_plugins import Plugin

from src import log
from src.bot import Bot

logger = log.get_logger(__name__)

plugin = Plugin[Bot]()


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


@plugin.slash_command(name="avatar")
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


setup, teardown = plugin.create_extension_handlers()
