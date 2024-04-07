import disnake


async def application_webhook(
    inter: disnake.GuildCommandInteraction,
    channel: disnake.TextChannel | None = None,
) -> disnake.Webhook:
    if not channel:
        channel = inter.channel
    webhooks = await channel.webhooks()
    for webhook in webhooks:
        if webhook.application_id == inter.bot.application_id:
            return webhook
    webhook = await channel.create_webhook(name=inter.bot.user.name)
    return webhook
