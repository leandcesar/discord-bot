import disnake
from disnake.ext import commands
from disnake_plugins import Plugin

from src import log
from src.bot import Bot

logger = log.get_logger(__name__)

plugin = Plugin[Bot]()


@plugin.listener("on_message")
async def on_message(message: disnake.Message) -> None:
    logger.debug(
        f"{message.guild} ({message.guild.id}) "
        f"#{message.channel} ({message.channel.id}) "
        f"@{message.author} ({message.author.id}): "
        f"{message.content!r} ({message.id})"
    )


@plugin.listener("on_command")
async def on_command(ctx: commands.Context[Bot]) -> None:
    logger.info(
        f"{ctx.guild} ({ctx.guild.id}) "
        f"#{ctx.channel} ({ctx.channel.id}) "
        f"@{ctx.author} ({ctx.author.id}): "
        f"{ctx.message.content} ({ctx.message.id})"
    )


@plugin.listener("on_slash_command")
async def on_slash_command(inter: disnake.GuildCommandInteraction) -> None:
    logger.info(
        f"{inter.guild} ({inter.guild.id}) "
        f"#{inter.channel} ({inter.channel.id}) "
        f"@{inter.author} ({inter.author.id}): "
        f"/{inter.application_command.qualified_name} {inter.options}"
    )


@plugin.listener("on_modal_submit")
async def on_modal_submit(inter: disnake.ModalInteraction) -> None:
    logger.info(
        f"{inter.guild} ({inter.guild.id}) "
        f"#{inter.channel} ({inter.channel.id}) "
        f"@{inter.author} ({inter.author.id}): "
        f"{inter.data}"
    )


@plugin.listener("on_command_error")
async def on_command_error(ctx: commands.Context[Bot], e: Exception) -> None:
    if isinstance(e, commands.errors.CommandNotFound):
        return None
    logger.error(
        f"{ctx.guild} ({ctx.guild.id}) "
        f"#{ctx.channel} ({ctx.channel.id}) "
        f"@{ctx.author} ({ctx.author.id}): "
        f"{ctx.message.content} ({ctx.message.id}) "
        f"{e}",
        exc_info=e,
    )


@plugin.listener("on_slash_command_error")
async def on_slash_command_error(inter: disnake.GuildCommandInteraction, e: Exception) -> None:
    logger.error(
        f"{inter.guild} ({inter.guild.id}) "
        f"#{inter.channel} ({inter.channel.id}) "
        f"@{inter.author} ({inter.author.id}): "
        f"/{inter.application_command.qualified_name} {inter.options} "
        f"{e}",
        exc_info=e,
    )


setup, teardown = plugin.create_extension_handlers()
