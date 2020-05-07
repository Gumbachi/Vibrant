import discord
from discord.ext import commands

from rapidfuzz import process

import database as db
from classes import Guild
from authorization import authorize
from converters import ThemeConverter
from cogs.color.color_assignment import color_user
from vars import bot


class ThemeAssignment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="theme.load", aliases=["t.l"])
    async def load_theme(self, ctx, *, theme: ThemeConverter):
        """Change the active colors to a theme."""
        authorize(ctx, "disabled", "roles", "themes", "heavy")
        guild = Guild.get(ctx.guild.id)

        msg = await ctx.send(embed=discord.Embed(title=f"Clearing colors..."))

        guild.heavy_command_active = ctx.command.name

        # clear colors
        await guild.clear_colors()

        # apply colors
        theme.activate()

        await msg.edit(embed=discord.Embed(title=f"Loading **{theme.name}**..."))

        async with ctx.channel.typing():
            for color in guild.colors:
                if not color.members:
                    continue

                for member in color.members:
                    await color_user(guild, member, color)

        # report success and update DB
        await msg.edit(embed=discord.Embed(title=f"Loaded **{theme.name}**",
                                           color=discord.Color.green()))
        await ctx.invoke(bot.get_command("colors"))
        guild.heavy_command_active = None
        db.update_prefs(guild)


def setup(bot):
    bot.add_cog(ThemeAssignment(bot))
