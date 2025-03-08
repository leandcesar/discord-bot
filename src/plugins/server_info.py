import disnake
from disnake.ext import commands
from disnake_plugins import Plugin

from src import log
from src.bot import Bot

logger = log.get_logger(__name__)

plugin = Plugin[Bot]()


def guild_has_banner(inter: disnake.GuildCommandInteraction) -> bool:
    return "BANNER" in inter.guild.features


@plugin.slash_command(name="server")
async def server_command(inter: disnake.GuildCommandInteraction) -> None:
    """
    ...  # TODO: add description
    """


async def server_icon_command(inter: commands.Context[commands.Bot] | disnake.GuildCommandInteraction) -> None:
    file = await inter.guild.icon.with_size(1024).to_file()
    if isinstance(inter, disnake.Interaction):
        await inter.edit_original_response(file=file)
    else:
        await inter.reply(file=file)


@plugin.command(name="servericon", aliases=["server"])
async def server_icon_prefix_command(ctx: commands.Context[commands.Bot]) -> None:
    await server_icon_command(ctx)


@server_command.sub_command(name="icon")
async def server_icon_slash_command(
    inter: disnake.GuildCommandInteraction,
) -> None:
    """
    ...  # TODO: add description
    """
    await inter.response.defer()
    await server_icon_command(inter)


async def server_banner_command(inter: commands.Context[commands.Bot] | disnake.GuildCommandInteraction) -> None:
    file = await inter.guild.banner.with_size(1024).to_file()
    if isinstance(inter, disnake.Interaction):
        await inter.edit_original_response(file=file)
    else:
        await inter.reply(file=file)


@commands.check(guild_has_banner)
@plugin.command(name="serverbanner")
async def server_banner_prefix_command(ctx: commands.Context[commands.Bot]) -> None:
    await server_banner_command(ctx)


@commands.check(guild_has_banner)
@server_command.sub_command(name="banner")
async def server_banner_slash_command(
    inter: disnake.GuildCommandInteraction,
) -> None:
    """
    ...  # TODO: add description
    """
    await inter.response.defer()
    await server_banner_command(inter)


setup, teardown = plugin.create_extension_handlers()
