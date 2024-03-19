# -*- coding: utf-8 -*-
import logging

from bot.core import config
from bot.core.bot import Bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-5s %(funcName)s:%(lineno)d %(message)s",
)
log = logging.getLogger()


if __name__ == "__main__":
    bot = Bot(
        debug=config.DEBUG,
        command_prefix=config.DISCORD_BOT_PREFIX,
        test_guilds=config.DISCORD_TEST_GUILD_IDS,
    )
    bot.load_all_cogs()
    bot.run(config.DISCORD_BOT_TOKEN)
