from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from cogs.color.manager import ColorManager


class RemoveModal(discord.ui.Modal):
    def __init__(self, manager: "ColorManager"):
        super().__init__(title="Remove a Color")
        self.manager = manager
        self.add_item(
            discord.ui.InputText(
                label="Color Index or Name", placeholder="ex. Hot Pink", min_length=1
            )
        )

    async def callback(self, interaction: discord.Interaction):

        index = self.children[0].value

        self.manager.remove_color(int(index))

        await interaction.response.edit_message(
            file=self.manager.snapshot, attachments=[]
        )
