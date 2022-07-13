import discord
from discord import ApplicationContext, slash_command
from common.database import db


class GeneralCommands(discord.Cog):
    """Handles all of the general commands like howdy."""

    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="howdy")
    async def howdy(self, ctx: ApplicationContext):
        """You've got a friend in me."""
        await ctx.respond(f"Howdy, {ctx.author.nick or ctx.author.name}!")


def setup(bot):
    bot.add_cog(GeneralCommands(bot))
