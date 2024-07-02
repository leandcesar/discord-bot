import disnake


class Select(disnake.ui.StringSelect):
    def __init__(self, *, callback, **kwargs) -> None:
        self._callback = callback
        super().__init__(**kwargs)

    async def callback(self, inter: disnake.MessageInteraction) -> None:
        await self._callback(inter, self.values[0])


class Dropdown(disnake.ui.View):
    def __init__(self, *, callback, timeout: float | None = 180.0, **kwargs) -> None:
        super().__init__(timeout=timeout)
        self.add_item(Select(callback=callback, **kwargs))


class Paginator(disnake.ui.View):
    def __init__(self, embeds: list[disnake.Embed], *, timeout: float | None = 180.0) -> None:
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.index = 0
        self._update_state()

    def _update_state(self) -> None:
        self.first_page.disabled = self.prev_page.disabled = self.index == 0
        self.last_page.disabled = self.next_page.disabled = self.index == len(self.embeds) - 1

    @disnake.ui.button(label="<<")
    async def first_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.index = 0
        self._update_state()
        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(label="<")
    async def prev_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.index -= 1
        self._update_state()
        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(label=">")
    async def next_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.index += 1
        self._update_state()
        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(label=">>")
    async def last_page(self, button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.index = len(self.embeds) - 1
        self._update_state()
        await inter.response.edit_message(embed=self.embeds[self.index], view=self)
