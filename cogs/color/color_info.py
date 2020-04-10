import io

import discord
from discord.ext import commands

from classes import Guild
from authorization import authorize, is_disabled
from utils import rgb_to_hex, to_sendable


class ColorInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="colors", aliases=["colours", "c"])
    async def show_colors(self, ctx):
        """Display an image of equipped colors."""
        authorize(ctx, "disabled", "colors")

        guild = Guild.get(ctx.guild.id)
        file = to_sendable(guild.draw_colors(), "colors")
        await ctx.send(file=file)

    @commands.command(name="info")
    async def show_color_info(self, ctx, *, query=""):
        authorize(ctx, "disabled", "colors")
        guild = Guild.get(ctx.guild.id)

        color = guild.find_color(query, threshold=0)

        members = (member.name for member in color.members)
        color_embed = discord.Embed(
            title=color.name,
            description=(f"Hexcode: {color.hexcode}\n"
                         f"RGB: {color.rgb}\n"
                         f"Members: {', '.join(members)}\n"
                         f"Index: {color.index}\n"
                         f"Role ID: {color.role_id}"),
            color=discord.Color.from_rgb(*color.rgb))

        await ctx.send(embed=color_embed)

    @commands.command(name="convert", aliases=["hex", "tohex"])
    async def convert_to_hex(self, ctx, *, rgb):
        """Converts RGB input to hex and send in channel"""
        authorize(ctx, "disabled")

        if "," in rgb:
            rgb = rgb.split(",")
        else:
            rgb = rgb.split(" ")

        # check for all channels
        if len(rgb) != 3:
            raise commands.UserInputError(
                f"Invalid input. try {ctx.prefix}convert 123, 123, 123")

        # veryify the inputs
        for val in rgb:
            if not val.isdigit():
                raise commands.UserInputError("All values must be numbers")
            val = int(val)
            if 0 > val > 255:
                raise commands.UserInputError(
                    "Numbers should be between 0-255")

        r, g, b = (int(val) for val in rgb)
        hexcode = rgb_to_hex((r, g, b))
        await ctx.send(f"{rgb} -> **{hexcode}**")


def setup(bot):
    bot.add_cog(ColorInfo(bot))
