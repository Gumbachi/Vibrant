from discord.ext import commands
import common.database as db


class GeneralCommands(commands.Cog):
    """Handles all of the simple commands such as saying howdy or
    the help command.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="howdy")
    async def howdy(self, ctx):
        """Says howdy!"""
        await ctx.send(f"Howdy, {ctx.message.author.mention}!")

    @commands.command(name="help")
    async def help(self, ctx):
        """The standard help command."""
        await ctx.send("Help dont exist yet")

    @commands.command(name="prefix", aliases=["vibrantprefix"])
    @commands.has_guild_permissions(manage_guild=True)
    async def change_server_prefix(self, ctx, *, new_prefix):
        """Change the bots prefix for the guild"""
        db.update_guild(ctx.guild.id, {"prefix": new_prefix})
        await ctx.send(f"New Prefix is `{new_prefix}`")

    @commands.command(name="get_id")
    async def get_guild_id(self, ctx):
        """fetches and prints the guilds id"""
        await ctx.send(str(ctx.guild.id))


def setup(bot):
    bot.add_cog(GeneralCommands(bot))
