from __future__ import annotations

import disnake

from src.bot import Bot

__all__ = ("application_webhook",)


async def application_webhook(
    bot: Bot, channel: disnake.TextChannel, /, *, reason: str | None = None
) -> disnake.Webhook:
    for webhook in await channel.webhooks():
        if webhook.application_id == bot.application_id:
            return webhook
    return await channel.create_webhook(name=bot.user.name, avatar=bot.user.avatar, reason=reason)
