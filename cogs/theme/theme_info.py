import io
import os
from os.path import sep
import json

import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

from classes import Guild
from authorization import authorize, is_disabled
from utils import hex_to_rgb, to_sendable, draw_imports
from sender import PaginatedImage


class ThemeInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="themes", aliases=["temes", "t"])
    async def show_themes(self, ctx):
        """Draw the guild's themes and send in channel."""
        authorize(ctx, "disabled", "themes")
        guild = Guild.get(ctx.guild.id)

        pages = PaginatedImage(content=guild.draw_themes(), pointer=0)
        await pages.send(ctx.channel)

    @commands.command(name="theme.info", aliases=["t.info", "t.i"])
    async def theme_info(self, ctx, *, query="1"):
        """Get general info about a theme."""
        authorize(ctx, "disabled", "themes")
        guild = Guild.get(ctx.guild.id)
        theme = guild.find_theme(query, threshold=0)

        # Puts colors in a list that shows name and members
        colors = ", ".join(
            [color.name + f"({len(color.member_ids)})" for color in theme.colors])

        # generate embed
        theme_embed = discord.Embed(
            title=theme.name,
            description=(
                f"Description: {theme.description}\n"
                f"Index: {theme.index}\n"
                f"Colors: {colors}"),
            color=discord.Color.blurple())
        await ctx.send(embed=theme_embed)

    @commands.command(name="imports", aliases=["presets"])
    async def show_imports(self, ctx):
        """Draw and send an image of all presets"""
        authorize(ctx, "disabled")

        pages = PaginatedImage(content=draw_imports(), pointer=0)
        await pages.send(ctx.channel)


def setup(bot):
    bot.add_cog(ThemeInfo(bot))
