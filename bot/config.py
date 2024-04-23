import json
from os import getenv

DEBUG = bool(getenv("DEBUG"))
LOG_LEVEL = getenv("LOG_LEVEL", "INFO")

BOT_TOKEN = getenv("BOT_TOKEN")
BOT_PREFIX = getenv("BOT_PREFIX")
BOT_TEST_DISCORD_GUILD_IDS: list[int] = json.loads(getenv("BOT_TEST_DISCORD_GUILD_IDS", "[]"))

IMAGGA_API_URL = getenv("IMAGGA_API_URL", "https://api.imagga.com")
IMAGGA_API_VERSION = getenv("IMAGGA_API_VERSION", "v2")
IMAGGA_API_KEY = getenv("IMAGGA_API_KEY")
IMAGGA_API_SECRET = getenv("IMAGGA_API_SECRET")
