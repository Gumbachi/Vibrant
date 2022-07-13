import math

import discord
from discord import ApplicationContext, slash_command

from common.database import db
from common.constants import NO_COLORS_EMBED
from utils.artist import draw_colors


class ColorInfo(discord.Cog):
    """Handles commands and listeners related to displaying colors"""

    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="colors")
    async def show_colors(self, ctx: ApplicationContext):
        """Display the active set of colors"""

        colors = db.get_colors(ctx.guild.id)

        if not colors:
            return await ctx.respond(embed=NO_COLORS_EMBED)

        image_file = draw_colors(colors)

        await ctx.respond(file=image_file)


def setup(bot: discord.Bot):
    bot.add_cog(ColorInfo(bot))
