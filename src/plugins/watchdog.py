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
        f"{message.content!r} ({message.id})",
        extra={"context": message},
    )


@plugin.listener("on_command")
async def on_command(ctx: commands.Context[Bot]) -> None:
    logger.info(
        f"{ctx.message.content} ({ctx.message.id})",
        extra={"context": ctx},
    )


@plugin.listener("on_slash_command")
async def on_slash_command(inter: disnake.GuildCommandInteraction) -> None:
    logger.info(
        f"/{inter.application_command.qualified_name} {inter.options}",
        extra={"context": inter},
    )


@plugin.listener("on_modal_submit")
async def on_modal_submit(inter: disnake.ModalInteraction) -> None:
    logger.info(
        f"{inter.data}",
        extra={"context": inter},
    )


@plugin.listener("on_command_error")
async def on_command_error(ctx: commands.Context[Bot], e: Exception) -> None:
    if isinstance(e, commands.errors.CommandNotFound):
        return None
    logger.error(
        f"{ctx.message.content} ({ctx.message.id}) {e}",
        extra={"context": ctx},
        exc_info=e,
    )


@plugin.listener("on_slash_command_error")
async def on_slash_command_error(inter: disnake.GuildCommandInteraction, e: Exception) -> None:
    logger.error(
        f"/{inter.application_command.qualified_name} {inter.options} {e}",
        extra={"context": inter},
        exc_info=e,
    )


setup, teardown = plugin.create_extension_handlers()
