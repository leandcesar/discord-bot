import datetime as dt
import os

import disnake
from disnake.ext import commands

from src import config, log
from src.util.localize import Localization

logger = log.get_logger(__name__)


class Bot(commands.Bot):
    def __init__(
        self,
        intents: disnake.Intents,
        allowed_mentions: disnake.AllowedMentions | None = None,
        *,
        reload: bool,
        prefix: str,
        owner_ids: set[int] | None = None,
        test_guilds: set[int] | None = None,
    ) -> None:
        super().__init__(
            intents=intents,
            allowed_mentions=allowed_mentions,
            command_prefix=commands.when_mentioned_or(prefix),
            owner_ids=owner_ids,
            reload=reload,
            test_guilds=test_guilds,
            help_command=None,
        )
        self.start_time: dt.datetime = dt.datetime.now(tz=dt.timezone.utc)
        self.localization = Localization(self.i18n)

    def load_extensions(self, path: str) -> None:
        for item in os.listdir(path):
            if "__" in item or not item.endswith(".py"):
                continue
            try:
                ext = f"src.extensions.{item[:-3]}"
                super().load_extension(ext)
            except commands.errors.NoEntryPointError as e:
                logger.critical(f"{e.name} has no setup function.")

    async def on_ready(self) -> None:
        logger.info(config.generate_startup_table(bot_name=self.user.name, bot_id=self.user.id))
        if config.Client.activity:
            activity = disnake.Activity(name=config.Client.activity, type=config.Client.activity_type)
            await self.change_presence(activity=activity, status=config.Client.activity_status)

    async def on_command(self, inter: commands.Context) -> None:
        logger.info(f"{inter.message.content!r} ({inter.message.id})", extra={"inter": inter})

    async def on_slash_command(self, inter: disnake.ApplicationCommandInteraction) -> None:
        logger.info(f"/{inter.application_command.qualified_name} {inter.options}", extra={"inter": inter})

    async def on_message_command(self, inter: disnake.MessageInteraction) -> None:
        logger.info(f"/{inter.application_command.qualified_name} {inter.options}", extra={"inter": inter})

    async def on_modal_submit(self, inter: disnake.ModalInteraction) -> None:
        logger.info(f"{inter.data}", extra={"inter": inter})

    async def on_command_error(self, inter: commands.Context, e: Exception) -> None:
        if isinstance(e, commands.errors.CommandNotFound):
            return None
        elif isinstance(e, commands.errors.MissingRequiredArgument):
            logger.warning(f"{inter.message.content!r} ({inter.message.id}) = {e}", extra={"inter": inter})
        else:
            logger.error(f"{inter.message.content!r} ({inter.message.id}) = {e}", extra={"inter": inter}, exc_info=e)
            await self.reply(inter, str(e))

    async def on_slash_command_error(self, inter: disnake.ApplicationCommandInteraction, e: Exception) -> None:
        if isinstance(e, commands.errors.MissingRequiredArgument):
            logger.warning(
                f"/{inter.application_command.qualified_name} {inter.options} = {e}",
                extra={"inter": inter},
            )
        else:
            logger.error(
                f"/{inter.application_command.qualified_name} {inter.options} = {e}",
                extra={"inter": inter},
                exc_info=e,
            )
            await self.reply(inter, str(e))

    async def on_message_command_error(self, inter: disnake.MessageInteraction, e: Exception) -> None:
        logger.error(
            f"/{inter.application_command.qualified_name} {inter.options} = {e}",
            extra={"inter": inter},
            exc_info=e,
        )
        await self.reply(inter, str(e))

    async def reply(
        self,
        inter: (
            disnake.Member
            | disnake.Message
            | disnake.TextChannel
            | commands.Context[commands.Bot]
            | disnake.ApplicationCommandInteraction
        ),
        /,
        content: str | None = None,
        **kwargs,
    ) -> disnake.Message | disnake.InteractionMessage | None:
        if isinstance(inter, disnake.Message | commands.Context):
            sender = inter.reply
        elif isinstance(inter, disnake.Interaction):
            sender = inter.edit_original_response if inter.response.is_done() else inter.send
        else:
            sender = inter.send
        logger.debug(f"{content!r}", extra={"inter": inter})
        return await sender(content, **kwargs)

    async def get_or_fetch_owners(self) -> list[disnake.User]:
        return [owner for owner_id in config.Client.owner_ids if (owner := await self.get_or_fetch_user(owner_id))]
