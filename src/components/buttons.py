import disnake


class ConfirmView(disnake.ui.View):
    def __init__(self, timeout: float | None = 180.0) -> None:
        super().__init__(timeout=timeout)
        self.value: bool | None = None

    @disnake.ui.button(label="✅", style=disnake.ButtonStyle.green)
    async def confirm_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.value = True
        self.stop()

    @disnake.ui.button(label="❌", style=disnake.ButtonStyle.red)
    async def cancel_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.value = False
        self.stop()


class DeleteView(disnake.ui.View):
    def __init__(self, timeout: float | None = 180.0) -> None:
        super().__init__(timeout=timeout)
        self.value: bool | None = None

    @disnake.ui.button(label="🗑️", style=disnake.ButtonStyle.red)
    async def delete_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.value = True
        self.stop()
