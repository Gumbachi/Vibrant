import discord
import docs
from discord import guild_only, option, slash_command
from discord.ext.pages import Paginator


class GeneralCommands(discord.Cog):
    """Handles all of the general commands/listeners like howdy."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    async def command_name_autocomplete(self, ctx: discord.AutocompleteContext):
        return [
            cmd.qualified_name for cmd in self.bot.walk_application_commands()
            if cmd.qualified_name.startswith(ctx.value)
        ]

    @slash_command(name="howdy")
    async def howdy(self, ctx: discord.ApplicationContext):
        """You've got a friend in me. For checking the bot's pulse"""
        await ctx.respond(f"Howdy, {ctx.author.display_name}!")

    @slash_command(name="report")
    @guild_only()
    @option("command", description="The name of the command that had an error", autocomplete=command_name_autocomplete)
    @option("message", description="Tell the developer how you really feel")
    @option("screenshot", description="A picture showing the problem if applicable", required=False)
    async def report(self, ctx: discord.ApplicationContext, command: str, message: str, screenshot: discord.Attachment):
        """You've found a problem and want something done about it."""
        gumbachi = self.bot.get_user(128595549975871488)

        embed = discord.Embed(
            title=f"Problem with {command}",
            description=f"{ctx.guild_id}\n{message}"
        )

        if screenshot:
            embed.set_image(url=screenshot.url)

        await gumbachi.send(embed=embed)
        await ctx.respond(embed=discord.Embed(
            title="Report Sent",
            description="Thanks for the feedback."
        ))

    @slash_command(name="help")
    async def guide(self, ctx: discord.ApplicationContext):
        """Explains how Vibrant works in detail."""
        paginator = Paginator(pages=docs.guide, timeout=None, author_check=False)
        paginator.remove_button("first")
        paginator.remove_button("last")
        await paginator.respond(ctx.interaction)

    # @discord.Cog.listener(name="on_guild_remove")
    # async def on_guild_remove(self, guild: discord.Guild):
    #     """Delete a guild's data. Will not fail if no guild data found."""
    #     db.delete_guild(id=guild.id)


def setup(bot: discord.Bot):
    bot.add_cog(GeneralCommands(bot))
