import asyncio

from spotdl.download.downloader import Downloader
from spotdl.types.album import Album
from spotdl.types.options import DownloaderOptions, SpotifyOptions
from spotdl.types.playlist import Playlist
from spotdl.types.song import Song
from spotdl.utils.config import DOWNLOADER_OPTIONS, SPOTIFY_OPTIONS
from spotdl.utils.console import generate_initial_config
from spotdl.utils.spotify import SpotifyClient

SINGLETON_SPOTIFY_CLIENT: SpotifyClient | None = None


class Spotify:
    def __init__(self) -> None:
        self.default_client_settings = SpotifyOptions(**SPOTIFY_OPTIONS)
        self.default_downloader_settings = DownloaderOptions(**DOWNLOADER_OPTIONS)
        self.default_downloader_settings["simple_tui"] = True
        global SINGLETON_SPOTIFY_CLIENT
        if SINGLETON_SPOTIFY_CLIENT is None:
            generate_initial_config()
            SINGLETON_SPOTIFY_CLIENT = SpotifyClient.init(**self.default_client_settings)
        self.client = SINGLETON_SPOTIFY_CLIENT

    async def fetch_album(self, album_url: str) -> Album:
        return await asyncio.to_thread(Album.from_url, album_url)

    async def fetch_playlist(self, playlist_url: str) -> Playlist:
        return await asyncio.to_thread(Playlist.from_url, playlist_url)

    async def fetch_song(self, song_url: str) -> Song:
        return await asyncio.to_thread(Song.from_url, song_url)

    async def download_song(
        self,
        song: Song,
        /,
        *,
        path: str | None = None,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> str:
        downloader_settings = self.default_downloader_settings.copy()
        if path:
            downloader_settings["output"] = f"{path}/{downloader_settings['output']}"
        try:
            downloader = Downloader(downloader_settings, loop=loop)
            song, filename = await downloader.pool_download(song)
            return filename
        except Exception as e:
            raise e
        finally:
            downloader.progress_handler.close()
