from __future__ import annotations

import datetime as dt
import json
import os

import disnake
from disnake.ext import commands, tasks

from src import constants, log
from src.util.http import APIHTTPClient
from src.util.localize import Localization

logger = log.get_logger(__name__)

__all__ = ("Bot",)


class Bot(commands.Bot):
    def __init__(
        self,
        intents: disnake.Intents,
        allowed_mentions: disnake.AllowedMentions | None = None,
        *,
        prefix: str,
        owner_ids: set[int],
        reload: bool,
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
        self.http_client: APIHTTPClient = APIHTTPClient()
        self.afk_data: dict[str, str] = {}
        self._deleted_message_history: list[disnake.Message] = []
        self._edited_message_history: list[disnake.Message] = []

    @property
    def deleted_messages(self) -> list[disnake.Message]:
        self._deleted_message_history = self._deleted_message_history[-100:]
        return self._deleted_message_history

    @property
    def edited_messages(self) -> list[disnake.Message]:
        self._edited_message_history = self._edited_message_history[-100:]
        return self._edited_message_history

    @property
    def afk_path_file(self) -> str:
        path_file = os.path.join(constants.Client.private_data_path, "afk.json")
        folder = os.path.dirname(path_file)
        if not os.path.exists(folder):
            os.makedirs(folder)
        if not os.path.exists(path_file):
            with open(path_file, mode="w") as f:
                f.write(json.dumps({}, indent=4))
        return path_file

    def load_afk_data(self):
        # NOTE: use `aiofiles` if experiencing issues with async write/read operations
        with open(self.afk_path_file) as f:
            self.afk_data = json.loads(f.read())

    def persist_afk_data(self) -> None:
        # NOTE: use `aiofiles` if experiencing issues with async write/read operations
        with open(self.afk_path_file, mode="w") as f:
            f.write(json.dumps(self.afk_data, indent=4))

    async def on_connect(self) -> None:
        pass

    async def on_ready(self) -> None:
        msg = constants.generate_startup_table(bot_name=self.user.name, bot_id=self.user.id)
        logger.info(msg)
        self.load_afk_data()
        self.loop_activities.start()

    @tasks.loop(minutes=5)
    async def loop_activities(self) -> None:
        if constants.Client.activities:
            activity = disnake.Activity(
                name=next(iter(constants.Client.activities_cycle)),
                type=constants.Client.activity_type,
            )
        elif len(constants.Client.activities) == 1:
            activity = disnake.Activity(
                name=constants.Client.activities[0],
                type=constants.Client.activity_type,
            )
            self.loop_activities.stop()
        else:
            logger.warning("There are no activities provided.")
            activity = None
            self.loop_activities.stop()

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
