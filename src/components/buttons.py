import disnake

__all__ = ("Confirm", "Delete")


class Confirm(disnake.ui.View):
    def __init__(self, timeout: float | None = 180.0) -> None:
        super().__init__(timeout=timeout)
        self.value: bool | None = None

    @disnake.ui.button(label="✅", style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.value = True
        self.stop()

    @disnake.ui.button(label="❌", style=disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.value = False
        self.stop()


class Delete(disnake.ui.View):
    def __init__(self, timeout: float | None = 180.0) -> None:
        super().__init__(timeout=timeout)
        self.value: bool | None = None

    @disnake.ui.button(label="🗑️", style=disnake.ButtonStyle.red)
    async def delete(self, button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.value = True
        self.stop()
