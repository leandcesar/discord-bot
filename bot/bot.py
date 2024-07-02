import datetime
import logging

import disnake
from disnake.ext import commands
from prisma import Prisma


class Bot(commands.Bot):
    def __init__(
        self,
        *,
        bot_prefix: str | None = None,
        debug: bool = False,
        logger_cls: logging.Logger = logging.getLogger(),
        logger_level: str | int = "INFO",
        **kwargs,
    ) -> None:
        command_sync_flags = commands.CommandSyncFlags.default()
        command_sync_flags.sync_commands_debug = debug
        intents = disnake.Intents.all()
        super().__init__(
            command_sync_flags=command_sync_flags,
            command_prefix=bot_prefix,
            intents=intents,
            reload=debug,
            asyncio_debug=debug,
            enable_debug_events=debug,
            help_command=None,
            strict_localization=True,
            **kwargs,
        )
        self._deleted_message_history: list[disnake.Message] = []
        self._edited_message_history: list[disnake.Message] = []
        self.db = Prisma()
        self.logger = logger_cls
        self.logger.setLevel(logger_level)
        self.started_at = datetime.datetime.utcnow()

    def connect_database(self) -> None:
        return self.loop.run_until_complete(self.db.connect())

    @property
    def deleted_messages(self) -> list[disnake.Message]:
        self._deleted_message_history = self._deleted_message_history[-100:]
        return self._deleted_message_history

    @property
    def edited_messages(self) -> list[disnake.Message]:
        self._edited_message_history = self._edited_message_history[-100:]
        return self._edited_message_history

    async def on_ready(self) -> None:
        self.logger.info(f"Logged in as @{self.user} ({self.user.id})")

    def localized(self, key: str, /, *, locale: disnake.Locale) -> str:
        i18n = self.i18n.get(key=key)
        try:
            locale_name = locale.name.replace("_", "-")
            return i18n[locale_name]
        except Exception:
            return i18n.values()[0]
