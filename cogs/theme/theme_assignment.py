import discord
from discord.ext import commands

import database as db
from classes import Guild
from authorization import authorize
from vars import bot, heavy_command_active
from cogs.color.color_assignment import color_user


class ThemeAssignment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="theme.load", aliases=["t.load", "t.l"])
    async def load_theme(self, ctx, *, query):
        """Change the active colors to a theme."""
        authorize(ctx, "disabled", "roles", "themes",
                  "heavy", theme_query=(query, 90))
        guild = Guild.get(ctx.guild.id)
        theme = guild.find_theme(query, 90)

        print("Loading theme")
        heavy_command_active[ctx.guild.id] = ctx.command.name

        # clear colors
        await guild.clear_colors()

        # apply colors
        theme.activate()

        await ctx.send(f"Loading the **{theme.name}** theme. This may take a while...")
        async with ctx.channel.typing():
            for color in guild.colors:
                if not color.members:
                    continue

                for member in color.members:
                    await color_user(guild, member, color)

        # report success and update DB
        await ctx.send(f"Loaded **{theme.name}**")
        await ctx.invoke(bot.get_command("colors"))
        del heavy_command_active[ctx.guild.id]
        db.update_prefs(guild)


def setup(bot):
    bot.add_cog(ThemeAssignment(bot))
