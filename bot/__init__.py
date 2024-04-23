try:
    from dotenv import load_dotenv
except ImportError:
    pass
else:
    load_dotenv()

from .version import __version__  # noqa
