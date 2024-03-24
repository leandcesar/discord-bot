# -*- coding: utf-8 -*-
import logging
import os

import disnake
from disnake.ext import commands


class Bot(commands.Bot):
    def __init__(self, *, debug: bool = False, logger: logging.Logger, **kwargs) -> None:
        self.logger = logger
        if debug:
            self.logger.setLevel(logging.DEBUG)
        intents = disnake.Intents.default()
        intents.message_content = True
        command_sync_flags = commands.CommandSyncFlags.default()
        command_sync_flags.sync_commands_debug = debug
        super().__init__(
            intents=intents,
            command_sync_flags=command_sync_flags,
            reload=debug,
            asyncio_debug=debug,
            enable_debug_events=debug,
            **kwargs,
        )

    def load_all_cogs(self) -> None:
        for file in os.listdir("./bot/cogs"):
            if not file.endswith(".py"):
                continue
            try:
                extension = file[:-3]
                self.load_extension(f"bot.cogs.{extension}")
                self.logger.info(f"Loaded extension {extension!r}")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                self.logger.error(f"Failed to load extension {extension!r}\n{exception}")

    async def on_application_command(self, inter: disnake.ApplicationCommandInteraction) -> None:
        self.logger.info(f"{inter.guild} #{inter.channel} @{inter.author}: /{inter.data.name} {inter.options}")
        await self.process_application_commands(inter)

    async def on_slash_command_error(
        self, inter: disnake.ApplicationCommandInteraction, e: commands.errors.CommandError
    ) -> None:
        if self.extra_events.get("on_slash_command_error", None):
            return None
        command = inter.application_command
        if command and command.has_error_handler():
            return None
        cog = command.cog
        if cog and cog.has_slash_error_handler():
            return None
        self.logger.error(f"{type(e).__name__}: {e}")
