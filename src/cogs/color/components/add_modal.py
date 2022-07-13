from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from cogs.color.manager import ColorManager

from model.color import Color


class AddModal(discord.ui.Modal):
    def __init__(self, manager: "ColorManager"):
        super().__init__(title="Add a Color")
        self.manager = manager
        self.add_item(
            discord.ui.InputText(
                label="Color Name",
                placeholder="ex. Hot Pink",
                min_length=1,
                max_length=30,
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Hexcode - Optional if you fill in RGB",
                placeholder="ex. #FF69B4",
                min_length=4,
                max_length=7,
                required=False,
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="RGB - Optional if you fill in Hexcode",
                placeholder="ex. 255, 105, 180",
                min_length=6,
                max_length=13,
                required=False,
            )
        )

    async def callback(self, interaction: discord.Interaction):

        name = self.children[0].value
        hexcode = self.children[1].value
        rgb = self.children[2].value

        if not rgb and not hexcode:
            raise discord.InvalidArgument("You must provide a color value")

        color = Color(name, hexcode)

        success = self.manager.add_color(color)

        if not success:
            content = "Something went wrong, please try again"
        else:
            content = None

        await interaction.response.edit_message(
            content=content, file=self.manager.snapshot, attachments=[]
        )
