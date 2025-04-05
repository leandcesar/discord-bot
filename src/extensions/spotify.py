import asyncio
import os
import re
import shutil

import disnake
from disnake_plugins import Plugin

from src.bot import Bot
from src.components import spotify

plugin = Plugin[Bot]()

SPOTIFY_URL_REGEX = re.compile(r"https?://(?:www\.)?open.spotify.com/(?:intl-pt/)?track/\S+")


def get_latest_file(path: str) -> str | None:
    files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    if not files:
        return None
    return max(files, key=os.path.getmtime)


@plugin.load_hook()
async def fix_preview_load_hook() -> None:
    spotify.init()


@plugin.listener("on_message")
async def on_message(message: disnake.Message) -> None:
    if message.author.bot:
        return None
    spotify_url_match = SPOTIFY_URL_REGEX.search(message.content)
    if not spotify_url_match:
        return None
    track_url = spotify_url_match.group(0)
    path = f"temp/{message.id}"
    try:
        await asyncio.to_thread(spotify.download_track, track_url, path)
        filename = get_latest_file(path)
    except Exception as e:
        raise e
    else:
        await message.reply(file=disnake.File(filename))
    finally:
        if os.path.exists(path):
            shutil.rmtree(path)


setup, teardown = plugin.create_extension_handlers()
