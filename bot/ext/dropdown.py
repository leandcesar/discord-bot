import disnake


class Select(disnake.ui.StringSelect):
    def __init__(self, *, callback, **kwargs) -> None:
        self._callback = callback
        super().__init__(**kwargs)

    async def callback(self, inter: disnake.MessageInteraction) -> None:
        user_input = self.values[0]
        return await self._callback(inter, user_input)


class Dropdown(disnake.ui.View):
    def __init__(self, *, callback, **kwargs) -> None:
        super().__init__()
        self.add_item(Select(callback=callback, **kwargs))
