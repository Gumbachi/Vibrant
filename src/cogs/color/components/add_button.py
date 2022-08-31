
import database as db
import discord
import utils
from common.constants import MAX_COLORS
from model.color import Color
from utils.errors import InvalidColorValue

from ..responses import INVALID_COLOR_VALUE, MAX_COLORS_EMBED


class AddButton(discord.ui.Button):
    def __init__(self):
        super().__init__(emoji="➕")

    async def callback(self, interaction: discord.Interaction):

        if not interaction.user.guild_permissions.manage_roles:
            return await interaction.response.send_message(content="You dont have permission for that (Manage Roles)", ephemeral=True)

        # check for max colors
        colors = db.get_colors(interaction.guild.id)
        if len(colors) >= MAX_COLORS:
            return await interaction.response.send_message(embed=MAX_COLORS_EMBED, ephemeral=True)

        await interaction.response.send_modal(AddColorModal())


class AddColorModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Add a Color")
        self.add_item(
            discord.ui.InputText(
                label="Name",
                placeholder='ex. "Best Color Ever" or "Red"',
                min_length=1,
                max_length=99,
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Color Value",
                placeholder='ex. "#7289DA" or "114, 137, 218"'
            )
        )

    async def callback(self, interaction: discord.Interaction):

        name = self.children[0].value
        value = self.children[1].value

        try:
            color = Color(name=name, hexcode=value, role=None)
        except utils.InvalidColorValue:
            return await interaction.response.send_message(embed=INVALID_COLOR_VALUE, ephemeral=True)

        db.add_color(interaction.guild.id, color)

        colors = db.get_colors(interaction.guild.id)
        snapshot = utils.draw_colors(colors)

        await interaction.response.edit_message(file=snapshot, attachments=[], embed=None)
