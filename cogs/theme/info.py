import io
import os
from os.path import sep
import json

from discord import Embed, File
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

import common.database as db


class ThemeInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="themes", aliases=["temes", "t"])
    async def show_themes(self, ctx):
        """Draw the guild's themes and send in channel."""
        themes = db.get(ctx.guild.id, "themes")

        if not themes:
            return await ctx.send(embed=Embed(title="You have no themes"))

        await ctx.send("Not finished yet")

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

        await ctx.send("Not Finished")


def setup(bot):
    bot.add_cog(ThemeInfo(bot))
