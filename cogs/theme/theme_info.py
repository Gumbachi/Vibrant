import io
import os
from os.path import sep
import json

import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

from classes import Guild
from authorization import authorize, is_disabled
from functions import hex_to_rgb


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
    async def show_imports(self, ctx, *,  page=1):
        """Draw and send an image of all presets"""
        authorize(ctx, "disabled")

        color_height = 44  # height of color boxes
        cont_height = 112 + 7  # container height
        canvas_width = 900
        padding_above_text = 20
        padding_below_text = 10
        box_margin = 5

        presets = os.listdir(f"presets{sep}")
        rows = len(presets)

        img = Image.new(mode='RGBA',
                        size=(canvas_width, cont_height * rows),
                        color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)  # set image for drawing

        # set font
        fnt = ImageFont.truetype(
            f"assets{os.path.sep}Roboto.ttf",
            size=40)

        # draws themes
        for i, filename in enumerate(presets):
            preset = json.load(open(f"presets{sep}{filename}", "r"))

            # draw text
            msg = f"{preset['name']}: {preset['description']}"
            text_width, text_height = draw.textsize(msg, fnt)

            # text coords
            x = (canvas_width/2)-(text_width/2)  # center
            y = i * cont_height + padding_above_text

            text_height += padding_above_text + padding_below_text

            draw.text((x, y), msg, font=fnt, fill=(255, 255, 255))

            width_of_rect = canvas_width/len(preset["colors"])

            # draw color preview
            for j, color in enumerate(preset["colors"], 0):
                # top left corner
                x0 = j * width_of_rect
                y0 = i * cont_height + text_height

                # bottom right corner
                x1 = x0 + width_of_rect - box_margin
                y1 = y0 + color_height

                value = hex_to_rgb(color["hexcode"])
                draw.rectangle([(x0, y0), (x1, y1)], fill=value)

        # return binary data
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='WEBP')
        byte_arr = byte_arr.getvalue()
        file = discord.File(io.BytesIO(byte_arr), filename="imports.webp")
        await ctx.send(file=file)


def setup(bot):
    bot.add_cog(ThemeInfo(bot))
