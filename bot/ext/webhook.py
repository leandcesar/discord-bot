import disnake

from bot import Bot


async def application_webhook(bot: Bot, channel: disnake.TextChannel, /) -> disnake.Webhook:
    for webhook in await channel.webhooks():
        if webhook.application_id == bot.application_id:
            return webhook
    return await channel.create_webhook(name=bot.user.name)
