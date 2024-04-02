import disnake


class Profile(disnake.Embed):
    def __init__(self, *, member: disnake.Member, user: disnake.User, **kwargs) -> None:
        title = f"`{member.display_name}` aka. `{member.global_name}`, `{member.name}`"
        if isinstance(member.activity, disnake.Spotify):
            description = (
                f"[**{member.activity.title}** from {member.activity.artists}]({member.activity.track_url})"
            )
        elif isinstance(member.activity, disnake.Streaming):
            description = f"[**{member.activity.game}** from @{member.activity.twitch_name}]({member.activity.url})"
        elif member.activity:
            description = member.activity.name
        else:
            description = ""
        super().__init__(
            title=title,
            description=description,
            color=member.color,
            url=user.display_avatar.url,
        )
        if user.display_avatar:
            self.set_thumbnail(user.display_avatar.url)
        if user.banner:
            self.set_image(user.banner.url)
        self.add_field("Cor", f"`{member.color}`")
        self.add_field("Criado em", f"<t:{int(member.created_at.timestamp())}:d>")
        self.add_field("Entrou em", f"<t:{int(member.joined_at.timestamp())}:d>")
        self.add_field("Cargos", " ".join([role.mention for role in member.roles[1:][::-1]]), inline=False)
