# -*- coding: utf-8 -*-
import disnake


async def get_webhook(inter: disnake.GuildCommandInteraction) -> disnake.Webhook | None:
    webhooks = await inter.channel.webhooks()
    for webhook in webhooks:
        if webhook.application_id == inter.bot.application_id:
            return webhook
    return None


async def create_webhook(inter: disnake.GuildCommandInteraction) -> disnake.Webhook:
    return await inter.channel.create_webhook(name=inter.bot.user.name)


async def get_or_create_webhook(inter: disnake.GuildCommandInteraction) -> disnake.Webhook:
    return await get_webhook(inter) or await create_webhook(inter)
