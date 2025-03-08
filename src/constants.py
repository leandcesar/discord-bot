from __future__ import annotations

import datetime as dt
import json
import os
import typing as t
from itertools import cycle
from sys import version as system_version

import disnake
from disnake import __version__ as disnake_version

from src import __version__ as bot_version

if t.TYPE_CHECKING:
    from disnake import Permissions

try:
    import dotenv
except ModuleNotFoundError:
    pass
else:
    if dotenv.find_dotenv():
        dotenv.load_dotenv(override=True)

__all__ = (
    "Client",
    "generate_startup_table",
)


class Client:
    prefix = os.getenv("BOT_PREFIX", "%")
    owner_ids: tuple[int, ...] = ()  # User: { id }
    test_guilds: tuple[int, ...] = tuple(json.loads(os.getenv("TEST_GUILDS", "[]")))  # Guild: { id }
    token: str | None = os.getenv("TOKEN")

    reload = True

    admin_permissions: Permissions = disnake.Permissions(administrator=True)
    standard_permissions: Permissions = disnake.Permissions(
        change_nickname=True,
        create_instant_invite=True,
        read_messages=True,
        view_channel=True,
        add_reactions=True,
        attach_files=True,
        embed_links=True,
        read_message_history=True,
        send_messages=True,
        send_messages_in_threads=True,
        use_external_emojis=True,
        connect=True,
        speak=True,
    )

    activities = cycle(["fundo do poço"])
    activity_type = disnake.ActivityType.watching
    activity_status = disnake.Status.online


class Log:
    level: str = os.getenv("LOG_LEVEL", "INFO")


class AFK:
    path = "data/"  # WARNING: if changed, add to .gitignore and update in docker-compose.yml
    filename = "afk.json"


def generate_startup_table(bot_name: str, bot_id: int) -> str:
    now = dt.datetime.now(tz=dt.timezone.utc)
    return "\n".join(
        [
            "Started: " + now.strftime("%m/%d/%Y - %H:%M:%S"),
            "System Version: " + system_version,
            "Disnake Version: " + disnake_version,
            "Bot Version: " + bot_version,
            "Connected as: " + f"{bot_name} ({bot_id})",
        ],
    )
