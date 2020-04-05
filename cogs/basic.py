import discord
from discord.ext import commands

from classes import Guild
import database as db
from authorization import authorize, is_disabled
from vars import bot, change_log, get_commands, get_help, get_prefix


class BaseCommands(commands.Cog):
    """Handles all of the simple commands such as saying howdy or
    the help command. These commands are unrelated to anything
    color-related and most work in disabled channels
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx, page=None):
        """The standard help command.

        Pulls info from vars.py and allows
        users to select pages or specific commands.
        """

        # get prefix and generate help dictionary
        p = get_prefix(bot, ctx.message)
        help_dict = get_help(p)

        # Table of contents
        if not page:
            recipient = ctx
            title = "Vibrant Help"
            description = f"""Table of Contents.
                To go to another page please use `{p}help <page>`
                Example `{p}help 1`, `{p}help setup`"""
            fields = help_dict["Help"].items()

        # setup instructions/how to use
        elif page == '1' or page == 'setup':
            recipient = ctx.author
            title = "Vibrant Setup"
            description = "Follow these steps to learn how to use Vibrant"
            fields = help_dict["Setup"].items()

        # list of theme commands and short descriptions
        elif page == '2' or page == 'themes':
            recipient = ctx.author
            title = "Vibrant Themes Tutorial"
            description = "All you need to know about using themes with Vibrant"
            fields = help_dict["Themes"].items()

        # list of command and short descriptions
        elif page == '3' or page == 'general':
            recipient = ctx.author
            title = "Vibrant General Commands"
            description = ("A list of commands the bot has. For more info "
                           f"on a specific command you can use `{p}help <command>`"
                           f"Example: `{p}help prefix`")
            fields = help_dict["Commands"].items()

        # list of theme commands and short descriptions
        elif page == '4' or page == 'color':
            recipient = ctx.author
            title = "Vibrant Color Commands"
            description = ("A list of color commands the bot has. For more info "
                           f"on a specific command you can use `{p}help <command>`"
                           f"Example: `{p}help add`")
            fields = help_dict["Color Commands"].items()

        # list of theme commands and short descriptions
        elif page == '5' or page == 'theme':
            recipient = ctx.author
            title = "Vibrant Theme Commands"
            description = ("A list of theme commands the bot has. For more info "
                           f"on a specific command you can use `{p}help <command>`"
                           f"Example: `{p}help theme.overwrite`")
            fields = help_dict["Theme Commands"].items()

        # individual command help
        elif page in [command.name for command in bot.commands]:
            recipient = ctx
            cmd_list = get_commands(p)
            title = f"{p}{page}"
            description = cmd_list[page]["Description"]
            del cmd_list[page]["Description"]
            fields = cmd_list[page].items()

        # page not found
        else:
            raise commands.UserInputError(f"{page} is not a valid argument")

        # generate embed
        help_embed = discord.Embed(title=title, description=description,
                                   color=discord.Colour.blue())
        for k, v in fields:
            help_embed.add_field(name=k, value=v, inline=False)

        # notify user of DM
        if is_disabled(ctx.channel):
            await ctx.message.delete()
            recipient = ctx.author
        else:
            if recipient is ctx.author:
                await ctx.send("You've got mail!")

        # send message
        await recipient.send(embed=help_embed)

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


def setup(bot):
    bot.add_cog(BaseCommands(bot))
