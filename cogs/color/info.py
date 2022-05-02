import discord
from discord import ApplicationContext, slash_command


class ColorInfo(discord.Cog):
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
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
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

    @slash_command(name="colors")
    async def show_colors(self, ctx: ApplicationContext):
        """Display the active theme's colors."""

        # TODO Fetch Colors
        colors = None

        if not colors:
            no_colors_embed = discord.Embed(title="You have no colors :(")
            return await ctx.respond(embed=no_colors_embed)

        await ctx.respond("TODO Respond with file")


def setup(bot: discord.Bot):
    bot.add_cog(ColorInfo(bot))
