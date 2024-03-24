# -*- coding: utf-8 -*-
from bot.core import config
from bot.core.bot import Bot
from bot.core.logger import logger

if __name__ == "__main__":
    bot = Bot(
        debug=config.DEBUG,
        command_prefix=config.DISCORD_BOT_PREFIX,
        test_guilds=config.DISCORD_TEST_GUILD_IDS,
        logger=logger,
    )
    bot.load_all_cogs()
    bot.run(config.DISCORD_BOT_TOKEN)
