import random
import re

import discord
from discord.ext import commands
from fuzzywuzzy import fuzz, process

from classes import Color, Guild
from functions import check_hex, is_disabled, update_prefs, find_user
from vars import bot, change_log, get_commands, get_help, get_prefix


class BaseCommands(commands.Cog):
    """Handles all of the simple commands such as saying howdy or
    the help command. These commands are unrelated to anything
    color-related and most work in disabled channels
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx, arg=None):
        """The standard help command. Pulls info from vars.py and allows
         users to select pages or specific commands"""

        # check if channel is disabled
        disabled = is_disabled(ctx.channel)
        if disabled:
            if not isinstance(ctx.channel, discord.channel.DMChannel):
                await ctx.message.delete()

        # get prefix and generate help dictionary
        p = get_prefix(bot, ctx.message)
        help_dict = get_help(p)

        # Table of contents
        if not arg:
            recipient = ctx.author if disabled else ctx
            title = "Vibrant Help"
            description = f"""Table of Contents.
                To go to another page please use `{p}help <page number>`
                Example `{p}help 1`"""
            fields = help_dict[None].items()

        # setup instructions/how to use
        elif arg == '1' or arg == 'setup':
            recipient = ctx.author
            title = "VIbrant Setup"
            description = "Follow these steps to learn how to use Vibrant"
            fields = help_dict[1].items()

        # list of command and short descriptions
        elif arg == '2' or arg == 'commands':
            recipient = ctx.author
            title = "Vibrant Commands"
            description = ("A list of commands the bot has. For more info "
                          f"on a specific command you can use `{p}help <command>`"
                          f"Example: `{p}help add`")
            fields = help_dict[2].items()

        # individual command help
        elif arg in [command.name for command in bot.commands]:
            recipient = ctx.author if disabled else ctx
            cmd_list = get_commands(p)
            title = f"{p}{arg}"
            description = f"An in-depth description of the `{p}{arg}` command"
            fields = cmd_list[arg].items()
        else:
            raise commands.UserInputError(f"{arg} is not a valid argument")

        # generate embed
        help_embed = discord.Embed(title=title, description=description,
                                   color=discord.Colour.blue())
        for k, v in fields:
            help_embed.add_field(name=k, value=v, inline=False)

        # notify user of DM
        if recipient is ctx.author and not disabled:
            await ctx.send("You've got mail!")

        await recipient.send(embed=help_embed)

    @commands.command(name='howdy')
    async def howdy(self, ctx):
        """Says howdy! Will send in DMs if channel is disabled"""
        if is_disabled(ctx.channel):
            await ctx.author.send(f"Howdy, {ctx.message.author.mention}!")
        else:
            await ctx.send(f"Howdy, {ctx.message.author.mention}!")

    @commands.command(name='prefix', aliases=['vibrantprefix'])
    async def change_prefix(self, ctx, new_prefix=None):
        """Changes the server prefix and updates the database

        Args:
            new_prefix (str): the new prefix
        """
        # check user permissions
        if not ctx.author.guild_permissions.manage_guild:
            return await ctx.send(
                (f"{ctx.author.mention}, you need "
                 "`manage server` permissions to use this command"))

        # check channel status
        if is_disabled(ctx.channel):
            return await ctx.message.delete()

        guild = Guild.get_guild(ctx.guild.id)
        if not new_prefix:
            return await ctx.send(f"Current Prefix: `{guild.prefix}`")

        guild.prefix = new_prefix  # set new prefix
        await ctx.send(f"New Prefix is `{new_prefix}`")
        await update_prefs([guild])

    @commands.command("expose", aliases=['whois'])
    async def expose_user(self, ctx, *name):
        """Displays and embed giving simple information about a user"""
        user = " ".join(name)
        guild = Guild.get_guild(ctx.guild.id)

        # find a user
        if user == "":
            user = ctx.author
        else:
            user = find_user(ctx.message, user, ctx.guild, 0)

        if not user:
            return await ctx.send("Couldn't find user")

        #set color and name depending if user is colored
        if color_role := guild.get_color_role(user):
            color_name = color_role.name
            disc_color = color_role.color
        else:
            color_name = "None"
            disc_color = discord.Color.light_grey()

        # generate embed
        expose_embed = discord.Embed(title=f"{user.name}#{user.discriminator}",
                                     description=' ',
                                     color=disc_color)

        nickname = user.nick if user.nick else user.name

        # structure embed
        expose_embed.set_author(name=nickname, icon_url=user.avatar_url)
        expose_embed.add_field(name="Color", value=color_name)
        expose_embed.add_field(name='Status', value=str(user.status))
        expose_embed.add_field(name='Member Since', value=str(user.joined_at)[:10])
        expose_embed.set_thumbnail(url=user.avatar_url)
        expose_embed.set_footer(text=f"ID: {user.id}")

        # send to right location
        if is_disabled(ctx.channel):
            await ctx.message.delete()
            await ctx.author.send(embed=expose_embed)
        else:
            await ctx.send(embed=expose_embed)

    @commands.command("channels", aliases=["data"])
    async def channel_data(self, ctx):
        """Displays a list of channels that are enabled and disabled"""
        guild = Guild.get_guild(ctx.guild.id)

        #get welcome channel name
        if guild.welcome_channel:
            welcome = guild.get_welcome().name
        else:
            welcome = "None"

        # get names of disabled/enabled channels
        disabled = [channel.name for channel in guild.get_disabled()]
        enabled = [channel.name for channel in guild.get_enabled()]

        # build embed
        embed = discord.Embed(
            title=guild.name, description=f"Welcome Channel: `{welcome}`")
        embed.add_field(name="Enabled Channels",
                        value="\n".join(enabled) if enabled else "None")
        embed.add_field(name="Disabled Channels",
                        value="\n".join(disabled) if disabled else "None")

        # check if channel is disabled to choose where to send
        if is_disabled(ctx.channel):
            await ctx.message.delete()
            await ctx.author.send(embed=embed)
        else:
            await ctx.send(embed=embed)

    @commands.command(name="version", aliases=["patchnotes"])
    async def patchnotes(self, ctx, version=None):
        """generate formatted embed of patchnotesto send to user"""
        latest = "1.0"

        # get correct version
        if version in change_log.keys():
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

        if is_disabled(ctx.channel):
            await ctx.message.delete()
            await ctx.author.send(embed=patch_embed)
        else:
            await ctx.send(embed=patch_embed)

    @commands.command(name="report")
    async def report(self, ctx, *msg):
        """Sends a message to the developer"""
        gumbachi = bot.get_user(128595549975871488)
        report_embed = discord.Embed(
            title=f"Report from {ctx.author.name} in {ctx.guild.name}",
            description=" ".join(msg),
            color=discord.Colour.blue())
        await gumbachi.send(embed=report_embed)

        if is_disabled(ctx.channel):
            await ctx.author.send("Message sent.")
        else:
            await ctx.send("Message sent.")


def setup(bot):
    bot.add_cog(BaseCommands(bot))
