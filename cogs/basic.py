import discord
from discord.ext import commands

from classes import Guild
import database as db
from authorization import authorize, is_disabled
import vars
from vars import bot, change_log, get_commands, get_help, get_prefix
from sender import PaginatedEmbed


class BaseCommands(commands.Cog):
    """Handles all of the simple commands such as saying howdy or
    the help command. These commands are unrelated to anything
    color-related and most work in disabled channels
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx, *, page="0"):
        """The standard help command.

        Pulls info from vars.py and allows
        users to select pages or specific commands.
        """

        # get prefix and generate help dictionary
        p = ctx.prefix
        help_dict = get_help(p)

        if not page.isdigit() or not -1 < int(page) < len(help_dict):
            raise commands.UserInputError(
                f"Invalid page number. Number must be between 0-{len(help_dict)-1}")

        pages = PaginatedEmbed(content=help_dict, pointer=int(page))

        if is_disabled(ctx.channel):
            if not isinstance(ctx.channel, discord.DMChannel):
                await ctx.message.delete()
            await ctx.author.send(embed=pages.generate_embed())
        else:
            await pages.send(ctx.channel)

    @commands.command(name='howdy')
    async def howdy(self, ctx):
        """Says howdy! Will send in DMs if channel is disabled"""
        if is_disabled(ctx.channel):
            await ctx.author.send(f"Howdy, {ctx.message.author.mention}!")
        else:
            await ctx.send(f"Howdy, {ctx.message.author.mention}!")

    @commands.command(name='prefix', aliases=['vibrantprefix'])
    async def change_prefix(self, ctx, *, new_prefix=None):
        """Change the server prefix."""
        authorize(ctx, "disabled", "server")  # check perms and channel status
        guild = Guild.get(ctx.guild.id)

        if not new_prefix:
            return await ctx.send(f"Current Prefix: `{guild.prefix}`")

        guild.prefix = new_prefix  # set new prefix
        await ctx.send(f"New Prefix is `{new_prefix}`")
        db.update_prefs(guild)

    @commands.command(name="version", aliases=["patchnotes"])
    async def patchnotes(self, ctx, version=None):
        """patchnotes to send"""
        authorize(ctx, "disabled")

        latest = "1.2"

        # get correct version
        if version in change_log:
            info = change_log[version]
        else:
            info = change_log[latest]
            version = latest

        # create and add to embed
        patch_embed = discord.Embed(
            title=f"Vibrant v{version} Patch Notes",
            description=(f"Current Version: {latest}\n"
                         f"Versions: {', '.join(change_log.keys())}"),
            color=discord.Colour.blue())

        for k, v in info.items():
            patch_embed.add_field(name=k, value=v, inline=False)

        patch_embed.set_thumbnail(url=bot.user.avatar_url)
        await ctx.send(embed=patch_embed)

    @commands.command(name="pages")
    async def pagetest(self, ctx):
        pages = PaginatedEmbed(content=vars.ex)
        await pages.send(ctx)


def setup(bot):
    bot.add_cog(BaseCommands(bot))
