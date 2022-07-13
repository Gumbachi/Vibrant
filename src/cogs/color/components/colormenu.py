from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from cogs.color.manager import ColorManager

from .add_modal import AddModal
from .remove_modal import RemoveModal


class Emoji:
    ADD = "➕"
    REMOVE = "➖"


class ColorMenu(discord.ui.View):
    def __init__(self, manager: "ColorManager"):
        super().__init__(timeout=None)
        self.manager = manager

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.manage_roles

    @discord.ui.button(emoji=Emoji.ADD)
    async def add(self, button: discord.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(AddModal(self.manager))

    @discord.ui.button(emoji=Emoji.REMOVE)
    async def remove(self, button: discord.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(RemoveModal(self.manager))

    @discord.ui.button(label="RN")
    async def rename(self, button: discord.Button, interaction: discord.Interaction):
        await interaction.response.send_message(content="TODO")

    @discord.ui.button(label="RC")
    async def recolor(self, button: discord.Button, interaction: discord.Interaction):
        await interaction.response.send_message(content="TODO")
