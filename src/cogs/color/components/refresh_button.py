import database as db
import discord
import utils

from ..responses import NO_COLORS_EMBED


class RefreshButton(discord.ui.Button):
    def __init__(self):
        super().__init__(emoji="🔃")

    async def callback(self, interaction: discord.Interaction):

        # check for max colors
        colors = db.get_colors(interaction.guild.id)

        if not colors:
            return await interaction.response.edit_message(embed=NO_COLORS_EMBED, attachments=[])

        snapshot = utils.draw_colors(colors)
        await interaction.response.edit_message(file=snapshot, attachments=[], embed=None)
