from bot import config
from bot.core import Bot, logger

bot = Bot(
    bot_prefix=config.BOT_PREFIX,
    debug=config.DEBUG,
    logger_cls=logger,
    logger_level=config.LOG_LEVEL,
    test_guilds=config.BOT_TEST_DISCORD_GUILD_IDS,
)

if __name__ == "__main__":
    bot.i18n.load("bot/locale")
    bot.load_extensions("bot/cogs")
    bot.run(config.BOT_TOKEN)
