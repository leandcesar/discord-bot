import logging

import disnake
from disnake.ext import commands


class Bot(commands.Bot):
    def __init__(
        self,
        *,
        debug: bool = False,
        logger: logging.Logger = logging.getLogger(),
        logger_level,
        prefix: str | None = None,
        test_guilds: list[int] | None = None,
        **kwargs,
    ) -> None:
        self.debug = debug
        self.logger = logger
        self.logger.setLevel(logger_level)
        command_sync_flags = commands.CommandSyncFlags.default()
        command_sync_flags.sync_commands_debug = self.debug
        command_prefix = commands.when_mentioned_or(prefix) if prefix else commands.when_mentioned
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
        )

    async def on_ready(self) -> None:
        self.logger.info(f"Logged in as {self.user}")

    async def on_application_command(self, inter: disnake.ApplicationCommandInteraction) -> None:
        self.logger.info(f"{inter.guild} #{inter.channel} @{inter.author}: /{inter.data.name} {inter.options}")
        await self.process_application_commands(inter)
