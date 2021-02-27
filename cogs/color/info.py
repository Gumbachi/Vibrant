import io
import math
from os.path import sep

from common.cfg import bot
import common.utils as utils
import common.database as db
from discord import Embed, File
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont


class ColorInfo(commands.Cog):
    """Handles commands and listeners related to displaying colors"""

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def draw_colors(colors):
        """Draw the colors in the current set"""
        rows = math.ceil(len(colors) / 3)  # amt of rows needed
        row_height = 50
        column_width = 300
        columns = 3

        img = Image.new(mode='RGBA',
                        size=(columns * column_width, rows * row_height),
                        color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)  # set image for drawing
        fnt = ImageFont.truetype(
            font=f".{sep}assets{sep}fonts{sep}Roboto.ttf", size=30)

        # draws and labels boxes
        for i, color in enumerate(colors):

            rgb = utils.to_rgb(color["hexcode"])

            # draw boxes
            rem = i % 3  # 0,1,2 repeating
            div = i//3  # increment every 3 elements
            x1 = column_width * rem
            x2 = row_height * div
            y1 = column_width * (rem+1)
            y2 = row_height * (div+1)
            draw.rectangle([x1, x2, y1, y2], fill=rgb,
                           outline=(0, 0, 0, 0), width=2)

            W, H = column_width*rem, row_height*div+10  # origin to draw boxes
            msg = f"{i + 1}. {color['name']}"
            w, _ = draw.textsize(msg, fnt)  # width of text

            # cut text until it fits
            text_size_limit = column_width - (column_width/10)
            while w > text_size_limit:
                msg = msg[:-2]
                w, _ = draw.textsize(msg, fnt)
                if w <= text_size_limit:
                    msg = msg + "..."

            # Make text readable
            r, g, b = rgb
            luminance = (0.299 * r + 0.587 * g + 0.114 * b)/255
            text_color = (0, 0, 0) if luminance > 0.5 else (240, 240, 240)

            # Draw text on boxes
            x = (column_width-w)/2 + W
            y = H
            draw.text((x, y), msg, font=fnt, fill=text_color)  # draw text

        # to discord sendable
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='PNG')
        byte_arr = byte_arr.getvalue()
        im = io.BytesIO(byte_arr)
        return File(im, filename="colors.png")

    @commands.command(name="colors", aliases=["colours", "c"])
    async def show_colors(self, ctx):
        """Display an image of equipped colors."""
        colors = db.get(ctx.guild.id, "colors")

        if not colors:
            return await ctx.send(embed=Embed(title="You have no colors"))

        await ctx.send(file=self.draw_colors(colors))

    @commands.command(name="colorinfo", aliases=["cinfo"])
    async def show_colors_in_detail(self, ctx):
        """Show what the database thinks colors are (For testing/support)."""
        colors = db.get(ctx.guild.id, "colors")
        cinfo = Embed(title="Detailed Color Info", description="")
        for color in colors:
            members = [bot.get_user(id).name for id in color["members"]]
            cinfo.add_field(
                name=color["name"],
                value=f"**ROLE:** {color['role']}\n**MEMBERS({len(members)}):** {', '.join(members)}")

        await ctx.send(embed=cinfo)


def setup(bot):
    bot.add_cog(ColorInfo(bot))
