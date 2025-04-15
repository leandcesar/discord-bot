import os
import re
import shutil

import disnake
from disnake_plugins import Plugin

from src import config
from src.api.spotify import Spotify
from src.bot import Bot as _Bot

SPOTIFY_SONG_URL_REGEX = re.compile(r"https?://(?:www\.)?open.spotify.com/(?:intl-pt/)?track/\S+")
SPOTIFY_ALBUM_URL_REGEX = re.compile(r"https?://(?:www\.)?open.spotify.com/(?:intl-pt/)?album/\S+")
SPOTIFY_PLAYLIST_URL_REGEX = re.compile(r"https?://(?:www\.)?open.spotify.com/(?:intl-pt/)?playlist/\S+")


class Bot(_Bot):
    spotify: Spotify


plugin = Plugin[Bot]()


@plugin.load_hook()
async def spotify_load_hook() -> None:
    plugin.bot.spotify = Spotify()
    if os.path.exists("temp/"):
        shutil.rmtree("temp/")


@plugin.listener("on_message")
async def on_message(message: disnake.Message) -> None:
    if message.author.bot:
        return None
    if message.content.startswith("-p"):
        return None

    song_url_match = SPOTIFY_SONG_URL_REGEX.search(message.content)
    album_url_match = SPOTIFY_ALBUM_URL_REGEX.search(message.content)
    playlist_url_match = SPOTIFY_PLAYLIST_URL_REGEX.search(message.content)

    if song_url_match:
        song_url = song_url_match.group(0)
        song = await plugin.bot.spotify.fetch_song(song_url)
        songs = [song]
    elif album_url_match:
        album_url = album_url_match.group(0)
        album = await plugin.bot.spotify.fetch_album(album_url)
        name = album.name
        songs = album.songs
    elif playlist_url_match:
        playlist_url = playlist_url_match.group(0)
        playlist = await plugin.bot.spotify.fetch_playlist(playlist_url)
        name = playlist.name
        songs = playlist.songs
    else:
        return None

    is_single = bool(len(songs) == 1)
    path = f"temp/{message.id}"
    if is_single:
        await message.add_reaction(config.Emoji.loading)
    else:
        thread = await message.channel.create_thread(name=name, message=message, auto_archive_duration=60)

    for song in songs[:100]:
        filename = await plugin.bot.spotify.download_song(song, path=path, loop=plugin.bot.loop)
        if is_single:
            await message.reply(file=disnake.File(filename))
            await message.clear_reaction(config.Emoji.loading)
        else:
            await thread.send(file=disnake.File(filename))

    if os.path.exists(path):
        shutil.rmtree(path)


setup, teardown = plugin.create_extension_handlers()
