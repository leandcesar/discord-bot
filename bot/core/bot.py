# -*- coding: utf-8 -*-
import os

import disnake
from disnake.ext import commands


class Bot(commands.Bot):
    def __init__(self, debug: bool, **kwargs) -> None:
        intents = disnake.Intents.default()
        intents.message_content = True
        command_sync_flags = commands.CommandSyncFlags.default()
        command_sync_flags.sync_commands_debug = debug
        super().__init__(intents=intents, command_sync_flags=command_sync_flags, reload=debug, **kwargs)

    def load_all_cogs(self) -> None:
        for filename in os.listdir("./bot/cogs"):
            if filename.endswith(".py"):
                self.load_extension(f"bot.cogs.{filename[:-3]}")
