import io
import os
from os.path import sep

import discord
from discord.ext import commands

from classes import Guild
from authorization import authorize, is_disabled


class ThemeInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="themes", aliases=["temes", "t"])
    async def show_themes(self, ctx):
        """Draw the guild's themes and send in channel."""
        authorize(ctx, "themes")
        guild = Guild.get(ctx.guild.id)
        img = guild.draw_themes()  # get sendable

        file = discord.File(img, filename="themes.webp")

        # send to author or channel depending on status
        if is_disabled(ctx.channel):
            await ctx.message.delete()
            return await ctx.author.send(f"**{ctx.guild.name}**:", file=file)
        return await ctx.send(file=file)

    @commands.command(name="theme.info", aliases=["t.info", "t.i"])
    async def theme_info(self, ctx, *, query="1"):
        """Get general info about a theme."""
        authorize(ctx, "disabled", "themes")
        guild = Guild.get(ctx.guild.id)
        theme = guild.find_theme(query, threshold=0)

        # generate embed
        theme_embed = discord.Embed(
            title=theme.name,
            description=(
                f"Description: {theme.description}\n"
                f"Index: {theme.index}\n"
                f"Colors: {', '.join([color.name for color in theme.colors])}"),
            color=discord.Color.blurple())
        await ctx.send(embed=theme_embed)

    @commands.command(name="imports", aliases=["presets"])
    async def show_imports(self, ctx):
        for preset in os.listdir(f".{sep}presets"):
            pass


def setup(bot):
    bot.add_cog(ThemeInfo(bot))
