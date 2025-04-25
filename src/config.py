from __future__ import annotations

import datetime as dt
import json
import os
import typing as t
from sys import version as system_version

import disnake
from disnake import __version__ as disnake_version

from src import __version__ as bot_version

if t.TYPE_CHECKING:
    from disnake import Permissions

try:
    import dotenv  # type: ignore
except ModuleNotFoundError:
    pass
else:
    if dotenv.find_dotenv():
        dotenv.load_dotenv(override=True)


class Client:
    prefix = os.getenv("BOT_PREFIX", "%")
    owner_ids: tuple[int, ...] = tuple(json.loads(os.getenv("OWNER_IDS", "[]")))  # User: { id }
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

    activity: str | None = None
    activity_type: disnake.ActivityType | None = None
    activity_status: disnake.Status | None = None


class Log:
    level: str = os.getenv("LOG_LEVEL", "INFO")


class Groq:
    api_key: str | None = os.getenv("GROQ_API_KEY")
    chat_completations_model = "llama-3.3-70b-versatile"
    transcriptions_model = "whisper-large-v3"
    temperature = 0.5
    max_completion_tokens = 512


class WitAI:
    access_token: str | None = os.getenv("WITAI_ACCESS_TOKEN")


class File:
    path = "data/"  # WARNING: if changed, add to .gitignore and update in docker-compose.yml
    afk = os.path.join(path, "afk.json")
    alias = os.path.join(path, "alias.json")
    reminder = os.path.join(path, "reminder.json")
    weather = os.path.join(path, "weather.json")


class Emoji:
    afk_turn_on = os.getenv("EMOJI_AFK_TURN_ON", "🔕")
    afk_turn_off = os.getenv("EMOJI_AFK_TURN_OFF", "🔔")
    remind_created = os.getenv("EMOJI_REMIND_CREATED", "📅")
    remind_delivered = os.getenv("EMOJI_REMIND_DELIVERED", "⏰")
    loading = os.getenv("EMOJI_LOADING", "⌛")


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
