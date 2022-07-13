import discord
from cogs.color.manager import ColorManager
from common.constants import NO_COLORS_EMBED
from common.database import db
from discord import ApplicationContext, slash_command


class ColorCommands(discord.Cog):
    """Handles commands and listeners related to displaying colors"""

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.instances = {}

    @slash_command(name="colors")
    async def show_colors(self, ctx: ApplicationContext):
        """Display the color manager"""

        colors = db.get_colors(ctx.guild.id)

        if not colors:
            return await ctx.respond(embed=NO_COLORS_EMBED)

        manager = self.instances.get(ctx.guild.id, ColorManager(colors))
        self.instances[ctx.guild.id] = manager

        await ctx.respond("Manage colors below")
        message = await ctx.send(file=manager.snapshot, view=manager.controls)
        await manager.set_message(message)


def setup(bot: discord.Bot):
    bot.add_cog(ColorCommands(bot))
