import disnake
from disnake.ext import commands
from disnake_plugins import Plugin

from src.bot import Bot
from src.util import asset

plugin = Plugin[Bot]()


async def _avatar_command(
    inter: commands.Context[Bot] | disnake.ApplicationCommandInteraction,
    *,
    members: tuple[disnake.Member | disnake.User, ...],
) -> None:
    if len(members) == 1:
        file = await members[0].display_avatar.with_size(1024).to_file()
        await plugin.bot.reply(inter, file=file)
    else:
        avatars = [await member.display_avatar.with_size(1024).read() for member in members]
        with asset.concatenate_assets(avatars, columns=len(members), rows=1) as image_bytes:
            file = disnake.File(image_bytes, filename="avatars.png")
            await plugin.bot.reply(inter, file=file)


@plugin.command(name="avatar", description="Display the specified member's avatar(s).")
async def avatar_prefix_command(
    ctx: commands.Context[Bot],
    *members: disnake.Member | disnake.User,
) -> None:
    if not members:
        members = (ctx.author,)
    await _avatar_command(ctx, members=members)


@plugin.slash_command(name="avatar")
async def avatar_slash_command(
    inter: disnake.ApplicationCommandInteraction,
    member: disnake.Member | disnake.User = commands.Param(lambda inter: inter.author),
) -> None:
    """
    Display the specified member's avatar(s).

    Parameters
    ----------
    member: The member whose avatar(s) will be retrieved and displayed.
    """
    await inter.response.defer()
    await _avatar_command(inter, members=(member,))


async def _banner_command(
    inter: commands.Context[Bot] | disnake.ApplicationCommandInteraction,
    *,
    member: disnake.Member | disnake.User,
) -> None:
    files = []
    user = await plugin.bot.fetch_user(member.id)
    if not user.banner:
        raise Exception()
    file = await user.banner.with_size(1024).to_file()
    files.append(file)
    await plugin.bot.reply(inter, files=files)


@plugin.command(name="banner", description="Display the specified member's banner.")
async def banner_prefix_command(
    ctx: commands.Context[Bot],
    *,
    member: disnake.Member | disnake.User | None = None,
) -> None:
    if member is None:
        member = ctx.author
    await _banner_command(ctx, member=member)


@plugin.slash_command(name="banner")
async def banner_slash_command(
    inter: disnake.ApplicationCommandInteraction,
    member: disnake.Member | disnake.User = commands.Param(lambda inter: inter.author),
) -> None:
    """
    Display the specified member's banner.

    Parameters
    ----------
    member: The member whose banner will be retrieved and displayed.
    """
    await inter.response.defer()
    await _banner_command(inter, member=member)


setup, teardown = plugin.create_extension_handlers()
