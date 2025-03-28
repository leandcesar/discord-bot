import typing as t

import disnake
from disnake.ext import commands
from disnake_plugins import Plugin

from src import log
from src.bot import Bot
from src.util import asset

logger = log.get_logger(__name__)

plugin = Plugin[Bot]()


async def _avatar_command(
    inter: commands.Context[commands.Bot] | disnake.GuildCommandInteraction,
    *,
    members: t.Sequence[disnake.Member],
) -> None:
    if len(members) == 1:
        file = await members[0].display_avatar.with_size(1024).to_file()

        if isinstance(inter, disnake.Interaction):
            await inter.edit_original_response(file=file)
        else:
            await inter.reply(file=file)
    else:
        avatars = []
        for member in members:
            avatar = await member.display_avatar.with_size(1024).read()
            avatars.append(avatar)
        with asset.concatenate_assets(avatars, columns=len(members), rows=1) as image_bytes:
            file = disnake.File(image_bytes, filename="avatars.png")

            if isinstance(inter, disnake.Interaction):
                await inter.edit_original_response(file=file)
            else:
                await inter.reply(file=file)


@plugin.command(name="avatar")
async def avatar_prefix_command(
    ctx: commands.Context[commands.Bot],
    *members: disnake.Member,
) -> None:
    if not members:
        members = (ctx.author,)
    await _avatar_command(ctx, members=members)


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
    await _avatar_command(inter, members=[member])


async def _banner_command(
    inter: commands.Context[commands.Bot] | disnake.GuildCommandInteraction,
    *,
    member: disnake.Member,
) -> None:
    files = []
    if member.banner:
        file = await member.banner.with_size(1024).to_file()
        files.append(file)

    if isinstance(inter, disnake.Interaction):
        await inter.edit_original_response(files=files)
    else:
        await inter.reply(files=files)


@plugin.command(name="banner")
async def banner_prefix_command(
    ctx: commands.Context[commands.Bot],
    *,
    member: disnake.Member = commands.Param(lambda ctx: ctx.author),
) -> None:
    await _banner_command(ctx, member=member)


@plugin.slash_command(name="banner")
async def banner_slash_command(
    inter: disnake.GuildCommandInteraction,
    member: disnake.Member = commands.Param(lambda inter: inter.author),
) -> None:
    """
    Display the specified member's banner in the highest available resolution.

    Parameters
    ----------
    member: The member whose banner will be retrieved and displayed.
    """
    await inter.response.defer()
    await _banner_command(inter, member=member)


setup, teardown = plugin.create_extension_handlers()
