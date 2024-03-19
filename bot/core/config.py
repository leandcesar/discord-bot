# -*- coding: utf-8 -*-
from os import environ

DEBUG = bool(environ.get("DEBUG"))
DISCORD_TEST_GUILD_IDS = list(map(int, environ["DISCORD_TEST_GUILD_IDS"].split(",")))
DISCORD_BOT_TOKEN = environ["DISCORD_BOT_TOKEN"]
DISCORD_BOT_PREFIX = environ.get("DISCORD_BOT_PREFIX", "!")
IMAGGA_API_URL = environ.get("IMAGGA_API_URL", "https://api.imagga.com")
IMAGGA_API_VERSION = environ.get("IMAGGA_API_VERSION", "v2")
IMAGGA_API_KEY = environ["IMAGGA_API_KEY"]
IMAGGA_API_SECRET = environ["IMAGGA_API_SECRET"]
