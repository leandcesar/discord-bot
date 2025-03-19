import typing as t

import disnake
from disnake.ext import commands
from disnake_plugins import Plugin

from src import log
from src.bot import Bot
from src.util import asset

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
    members: t.Sequence[disnake.Member],
    format: str | None = None,
) -> None:
    if len(members) == 1:
        file = await members[0].display_avatar.with_size(1024).to_file()
        if isinstance(inter, disnake.Interaction):
            await inter.edit_original_response(file=file)
        else:
            await inter.reply(file=file)
    else:
        avatars = []
        if format is None:
            format = f"{len(members)}x1"
        columns, rows = format.split("x")
        for member in members:
            avatar = await member.display_avatar.with_size(1024).read()
            avatars.append(avatar)
        with asset.concatenate_assets(avatars, columns=int(columns), rows=int(rows)) as image_bytes:
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
    await avatar_command(ctx, members=members)


@member_command.sub_command(name="avatar")
async def avatar_slash_command(
    inter: disnake.GuildCommandInteraction,
    member: disnake.Member = commands.Param(lambda inter: inter.author),
    member2: disnake.Member | None = None,
    member3: disnake.Member | None = None,
    member4: disnake.Member | None = None,
    member5: disnake.Member | None = None,
    member6: disnake.Member | None = None,
    member7: disnake.Member | None = None,
    member8: disnake.Member | None = None,
    member9: disnake.Member | None = None,
    member10: disnake.Member | None = None,
    format: str | None = None,
) -> None:
    """
    Display the specified member's avatar(s) in the highest available resolution.

    Parameters
    ----------
    member: The member whose avatar(s) will be retrieved and displayed.
    """
    await inter.response.defer()
    members = list(
        filter(
            lambda member: member is not None,
            [
                member,
                member2,
                member3,
                member4,
                member5,
                member6,
                member7,
                member8,
                member9,
                member10,
            ],
        )
    )
    await avatar_command(inter, members=members, format=format)


async def banner_command(
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
