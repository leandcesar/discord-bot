from __future__ import annotations

import datetime as dt
import os

import disnake
from disnake.ext import commands

from src import constants, log
from src.util.localize import Localization

logger = log.get_logger(__name__)

__all__ = ("Bot",)


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
        )
        self.start_time: dt.datetime = dt.datetime.now(tz=dt.timezone.utc)
        self.localization = Localization(self.i18n)

    async def on_connect(self) -> None:
        pass

    async def on_ready(self) -> None:
        logger.info(constants.generate_startup_table(bot_name=self.user.name, bot_id=self.user.id))
        if constants.Client.activity:
            activity = disnake.Activity(name=constants.Client.activity, type=constants.Client.activity_type)
            await self.change_presence(activity=activity, status=constants.Client.activity_status)

    def load_extensions(self, path: str) -> None:
        for item in os.listdir(path):
            if "__" in item or not item.endswith(".py"):
                continue
            try:
                ext = f"src.plugins.{item[:-3]}"
                super().load_extension(ext)
            except commands.errors.NoEntryPointError as e:
                logger.critical(f"{e.name} has no setup function.")

    async def get_or_fetch_owners(self) -> list[disnake.User]:
        return [
            owner for owner_id in constants.Client.owner_ids if (owner := await self.get_or_fetch_user(owner_id))
        ]
