from discord.ext import commands
import common.database as db
import docs.docs as docs
from .catalog import Catalog
from common.utils import check_emoji


class GeneralCommands(commands.Cog):
    """Handles all of the geeral commands like help."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="howdy")
    async def howdy(self, ctx):
        """Says howdy!"""
        await ctx.send(f"Howdy, {ctx.message.author.mention}!")

    @commands.command(name="help")
    async def help(self, ctx):
        """The standard help command."""
        catalog = Catalog(docs.help_book(ctx.prefix))
        await catalog.send(ctx.channel)

    @commands.command(name="prefix", aliases=["vibrantprefix"])
    @commands.has_guild_permissions(manage_guild=True)
    async def change_server_prefix(self, ctx, *, new_prefix):
        """Change the bots prefix for the guild."""
        db.guilds.update_one(
            {"_id": ctx.guild.id},
            {"$set": {"prefix": new_prefix}}
        )
        await ctx.send(f"Prefix changed to `{new_prefix}` {check_emoji()}")


def setup(bot):
    bot.add_cog(GeneralCommands(bot))
