import io
import math
import os
from os.path import sep
import json

from discord import Embed, File
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

import common.database as db
import common.utils as utils
from ..catalog import Catalog


class ThemeInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def draw_themes(themes):
        """Creates an image displaying themes."""
        canvas_width = 900
        canvas_height = 600

        slice_length = 5  # how many themes per page
        slice_amt = math.ceil(len(themes)/slice_length)  # Pages needed

        # Theme container distribution
        cont_height = canvas_height // slice_length
        # text is drawn at 10% of container height
        text_top = int(cont_height * .1)
        text_height = int(cont_height * .30)  # text is 30% of container
        # color is drawn at 50% of container height
        color_top = int(cont_height * .5)
        color_height = int(cont_height * .45)  # color is 40% of container

        fnt = ImageFont.truetype(
            font=f"assets{sep}fonts{sep}Roboto.ttf",
            size=text_height
        )

        theme_slices = [themes[i:i+slice_length]
                        for i in range(0, len(themes), slice_length)]

        theme_images = []
        for i, theme_slice in enumerate(theme_slices):
            # Create new blank image
            img = Image.new(
                mode='RGBA',
                size=(canvas_width, cont_height * len(theme_slice)),
                color=(0, 0, 0, 0)
            )
            draw = ImageDraw.Draw(img)  # set image for drawing

            # Draw each theme
            for j, theme in enumerate(theme_slice):
                index = i * slice_length + j + 1  # index 1, 2, 3, 4 etc
                text = f"{index}. {theme['name']}"

                # text coords (x, y) indicates top left corner of text
                text_width, text_height = draw.textsize(text, fnt)
                x = (canvas_width/2)-(text_width/2)  # centered text
                y = j * cont_height + text_top
                draw.text((x, y), text, font=fnt, fill=(240, 240, 240))

                color_width = canvas_width/len(theme["colors"])

                # Draw each color
                for k, color in enumerate(theme["colors"]):
                    # top left corner
                    x0 = k * color_width
                    y0 = j * cont_height + color_top
                    # bottom right corner
                    x1 = x0 + color_width - 5  # 5 is color spacing
                    y1 = y0 + color_height

                    draw.rectangle(
                        xy=[(x0, y0), (x1, y1)],
                        fill=utils.to_rgb(color["hexcode"])
                    )

            theme_images.append(img)
        return theme_images

    @commands.command(name="themes", aliases=["temes", "t"])
    async def show_themes(self, ctx):
        """Draw the guild's themes and send in channel."""
        themes = db.get(ctx.guild.id, "themes")

        if not themes:
            return await ctx.send(embed=Embed(title="You have no themes"))

        theme_files = self.draw_themes(themes)

        # create and send catalog
        catalog = Catalog(theme_files)
        await catalog.send(ctx.channel)

    @commands.command(name="themeinfo", aliases=["tinfo"])
    async def show_themes_in_detail(self, ctx):
        """Shows a detailed, textbased view of your themes."""
        themes = db.get(ctx.guild.id, "themes")
        themes_embed = Embed(title="Themes in Detail", description="")
        for theme in themes:
            colors = [f"**{color['name']}**: {color['hexcode']}"
                      for color in theme["colors"]]
            themes_embed.add_field(name=theme["name"], value="\n".join(colors))

        await ctx.send(embed=themes_embed)

    @commands.command(name="imports", aliases=["presets"])
    async def show_imports(self, ctx):
        """Draw and send an image of all presets"""
        themes = []
        for fname in os.listdir(f"assets{sep}presets{sep}"):
            with open(f"assets{sep}presets{sep}{fname}", "r") as preset:
                themes.append(json.load(preset))

        # Create catalog and send
        catalog = Catalog(self.draw_themes(themes))
        await catalog.send(ctx.channel)


def setup(bot):
    bot.add_cog(ThemeInfo(bot))
