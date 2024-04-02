import disnake


async def get_application_webhook(
    inter: disnake.GuildCommandInteraction,
    channel: disnake.TextChannel | None = None,
) -> disnake.Webhook:
    if not channel:
        channel = inter.channel
    webhooks = await channel.webhooks()
    for webhook in webhooks:
        if webhook.application_id == inter.bot.application_id:
            return webhook
    return await channel.create_webhook(name=inter.bot.user.name)
