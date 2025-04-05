import disnake
from disnake.ext import commands
from disnake_plugins import Plugin

from src.bot import Bot

plugin = Plugin[Bot]()


def guild_has_banner(inter: disnake.ApplicationCommandInteraction) -> bool:
    return "BANNER" in inter.guild.features


@plugin.slash_command(name="server")
async def server_slash_command(inter: disnake.ApplicationCommandInteraction) -> None: ...


async def _server_icon_command(inter: commands.Context[Bot] | disnake.ApplicationCommandInteraction) -> None:
    file = await inter.guild.icon.with_size(1024).to_file()
    await plugin.bot.reply(inter, file=file)


@plugin.command(name="servericon", aliases=["server"], description="Display the guild's icon.")
async def server_icon_prefix_command(ctx: commands.Context[Bot]) -> None:
    await _server_icon_command(ctx)


@server_slash_command.sub_command(name="icon")
async def server_icon_slash_command(
    inter: disnake.ApplicationCommandInteraction,
) -> None:
    """
    Display the guild's icon.
    """
    await inter.response.defer()
    await _server_icon_command(inter)


async def _server_banner_command(inter: commands.Context[Bot] | disnake.ApplicationCommandInteraction) -> None:
    file = await inter.guild.banner.with_size(1024).to_file()
    await plugin.bot.reply(inter, file=file)


@commands.check(guild_has_banner)
@plugin.command(name="serverbanner", description="Display the guild's banner.")
async def server_banner_prefix_command(ctx: commands.Context[Bot]) -> None:
    await _server_banner_command(ctx)


@commands.check(guild_has_banner)
@server_slash_command.sub_command(name="banner")
async def server_banner_slash_command(
    inter: disnake.ApplicationCommandInteraction,
) -> None:
    """
    Display the guild's banner.
    """
    await inter.response.defer()
    await _server_banner_command(inter)


setup, teardown = plugin.create_extension_handlers()
