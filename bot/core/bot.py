import logging
import time

import disnake
from disnake.ext import commands


class Bot(commands.Bot):
    def __init__(
        self,
        *,
        debug: bool = False,
        logger_cls: logging.Logger = logging.getLogger(),
        logger_level: str | int = "INFO",
        bot_prefix: str | None = None,
        test_guilds: list[int] | None = None,
        **kwargs,
    ) -> None:
        self.debug = debug
        self.logger = logger_cls
        self.logger.setLevel(logger_level)
        self.init_timestamp = int(time.time())
        command_sync_flags = commands.CommandSyncFlags.default()
        command_sync_flags.sync_commands_debug = self.debug
        command_prefix = commands.when_mentioned_or(bot_prefix) if bot_prefix else commands.when_mentioned
        intents = disnake.Intents.all()
        super().__init__(
            command_sync_flags=command_sync_flags,
            command_prefix=command_prefix,
            intents=intents,
            test_guilds=test_guilds,
            reload=self.debug,
            asyncio_debug=self.debug,
            enable_debug_events=self.debug,
            help_command=None,
            strict_localization=True,
            **kwargs,
        )

    def localized(self, key: str, *, locale: disnake.Locale) -> str:
        i18n = self.i18n.get(key=key)
        try:
            locale_name = locale.name.replace("_", "-")
            return i18n[locale_name]
        except Exception:
            return i18n.values()[0]

    async def on_ready(self) -> None:
        self.logger.info(f"Logged in as {self.user}")

    async def on_application_command(self, inter: disnake.ApplicationCommandInteraction) -> None:
        self.logger.info(f"{inter.guild} #{inter.channel} @{inter.author}: /{inter.data.name} {inter.options}")
        await self.process_application_commands(inter)

    async def on_slash_command_error(
        self, inter: disnake.ApplicationCommandInteraction, e: commands.CommandError
    ) -> None:
        self.logger.error(
            f"{inter.guild} #{inter.channel} @{inter.author}: /{inter.data.name} {inter.options}, {e}", exc_info=e
        )
