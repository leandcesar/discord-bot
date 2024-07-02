import json
import os

DEBUG: bool = bool(os.getenv("DEBUG"))
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

PATH_LOCALE: str = "bot/locale"
PATH_COGS: str = "bot/cogs"
PATH_LISTENERS: str = "bot/listeners"

BOT_TOKEN: str | None = os.getenv("BOT_TOKEN")
BOT_PREFIX: str | None = os.getenv("BOT_PREFIX")
BOT_TEST_DISCORD_GUILD_IDS: list[int] = json.loads(os.getenv("BOT_TEST_DISCORD_GUILD_IDS", "[]"))

IMAGGA_API_URL: str = os.getenv("IMAGGA_API_URL", "https://api.imagga.com")
IMAGGA_API_VERSION: str = os.getenv("IMAGGA_API_VERSION", "v2")
IMAGGA_API_KEY: str | None = os.getenv("IMAGGA_API_KEY")
IMAGGA_API_SECRET: str | None = os.getenv("IMAGGA_API_SECRET")

G4F_API_URL: str = os.getenv("G4F_API_URL", "http://g4f:1337")
G4F_API_VERSION: str = os.getenv("G4F_API_VERSION", "v1")
