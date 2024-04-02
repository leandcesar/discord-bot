from bot import config
from bot.core import Bot, logger

bot = Bot(
    debug=config.DEBUG,
    logger=logger,
    logger_level=config.LOG_LEVEL,
    prefix=config.DISCORD_BOT_PREFIX,
    test_guilds=config.DISCORD_TEST_GUILD_IDS,
)

if __name__ == "__main__":
    bot.load_extensions("bot/cogs")
    bot.run(config.DISCORD_BOT_TOKEN)
