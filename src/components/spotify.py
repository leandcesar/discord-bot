from spotdl.console.download import download
from spotdl.download.downloader import Downloader
from spotdl.types.options import DownloaderOptions, SpotifyOptions
from spotdl.utils.config import DOWNLOADER_OPTIONS, SPOTIFY_OPTIONS
from spotdl.utils.console import generate_initial_config
from spotdl.utils.spotify import SpotifyClient

SPOTIFY_CLIENT: SpotifyClient | None = None


def init() -> None:
    global SPOTIFY_CLIENT
    if SPOTIFY_CLIENT is None:
        generate_initial_config()
        spotify_settings = SpotifyOptions(**SPOTIFY_OPTIONS)
        SPOTIFY_CLIENT = SpotifyClient.init(**spotify_settings)


def download_track(track_url: str, path: str | None = None) -> None:
    downloader_settings = DownloaderOptions(**DOWNLOADER_OPTIONS)
    if path:
        downloader_settings["output"] = f"{path}/{downloader_settings['output']}"
    downloader_settings["simple_tui"] = True
    downloader = Downloader(downloader_settings)
    try:
        download(query=[track_url], downloader=downloader)
    except Exception as e:
        raise e
    finally:
        downloader.progress_handler.close()
