import sys
import traceback

import discord
from discord.ext import commands

import database as db
import authorization as auth
from classes import Guild
from vars import bot, get_prefix, get_commands


class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command."""

        p = ctx.prefix
        gumbachi = bot.get_user(128595549975871488)
        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            return

        ################ COMMAND ERROR HANDLING ################

        # Check for data and if not data make a blank entry
        if isinstance(error, auth.MissingGuild):
            data = db.find_guild(ctx.guild.id)
            if not data:
                guild = Guild(id=ctx.guild.id)
                await gumbachi.send(f"Missing guild Not Recovered {ctx.guild.id} {ctx.guild.name}")
                await ctx.send(f"Couldn't find data for {ctx.guild.name}, so a blank profile has been created.\n"
                               "Please try your command again and if this issue persists, please inform Gumbachi in the support server.")
                db.update_prefs(guild)
            else:
                await gumbachi.send("Try again")
                await ctx.send("Sorry, please try that command again.")
            return

        guild = Guild.get(ctx.guild.id)

        # Channel Disabled
        if isinstance(error, auth.ChannelDisabled):
            try:
                await ctx.message.delete()
                guild = Guild.get(ctx.guild.id)
                embed = discord.Embed(title=f"{ctx.channel.name} is disabled",
                                      description=(f"Enabled channels include:\n"
                                                   f"{', '.join([channel.mention for channel in guild.enabled_channels])}"))
                return await ctx.author.send(embed=embed)
            except:
                return

        # Missing Permissions
        elif isinstance(error, auth.MissingPermissions):
            return await ctx.send(f"You need `{error}` permissions to use that command")

        # Heavy Command Running
        elif isinstance(error, auth.HeavyCommandActive):
            return await ctx.send(f"**{error}** command is running right now. Please wait for it to finish")

        # No Colors Available
        elif isinstance(error, auth.NoAvailableColors):
            embed = discord.Embed(
                title="No Available Colors",
                description=f"You can add some with `{p}add` or load a preset with `{p}theme.load`.\nLearn more with the `{p}help` command")
            return await ctx.send(embed=embed)

        # No Themes Available
        elif isinstance(error, auth.NoAvailableThemes):
            embed = discord.Embed(
                title="No Available Themes",
                description=f"You can save your current colors with `{p}theme.save` or import a theme with {p}import.\nLearn more with the `{p}help` command")
            return await ctx.send(embed=embed)

        # Theme/Color limit reached
        elif isinstance(error, auth.LimitReached):
            return await ctx.send(f"You have reached the max amount of {error}. Please delete some to make room for more")

        ################ USER INPUT HANDLING ################

        elif isinstance(error, auth.InvalidHexcode):
            embed = discord.Embed(
                title="Invalid Hex Code",
                description=(f"{error} is not a valid color "
                             "[hex code](https://www.google.com/search?q=color+picker)"))
            return await ctx.send(embed=embed)

        elif isinstance(error, auth.InvalidName):
            return await ctx.send(error)

        elif isinstance(error, auth.NotFoundError):
            return await ctx.send(f"Could not find **{error}**")

        elif isinstance(error, auth.InvalidSwapQuery):
            return await ctx.send(error)

        elif isinstance(error, auth.UserMissingColorRole):
            return await ctx.send(f"{str(error)} does not have a color role")

        ################ DISCORD ERROR HANDLING ################

        elif isinstance(error, discord.HTTPException) and error.code == 50007:
            return await ctx.send(f"Couldn't DM {ctx.author.mention}. Probably has me blocked")

        elif isinstance(error, discord.HTTPException) and error.code == 50013:
            return await ctx.send(f"The bot is missing permissions. If the bot has all required permissions then clicking the role and hitting save changes may fix it")

        elif isinstance(error, discord.HTTPException) and error.code == 30005:
            return await ctx.send(f"You have too many roles(250). Delete some to make room for the color roles")

        elif isinstance(error, discord.errors.Forbidden):
            return await ctx.send(
                f"I don't have permission to do this. Make sure the bot has required permissions")

        elif isinstance(error, commands.MissingRequiredArgument):
            cmd_list = get_commands(p)
            description = cmd_list.get(
                ctx.command.name, {"Usage": "None"}).get("Usage", "None")
            embed = discord.Embed(
                title="Missing Arguments", description=f"Proper Format\n" + description)
            return await ctx.send(embed=embed)

        elif isinstance(error, commands.UserInputError):
            return await ctx.send(str(error))

        elif isinstance(ctx.channel, discord.channel.DMChannel):
            return await ctx.send(f"**{ctx.command}** must be used in a server channel")

        guild.heavy_command_active = None

        error_embed = discord.Embed(title=f'Your command: {ctx.message.content}',
                                    description=f"{ctx.guild.id}: {error}",
                                    color=discord.Colour.red())
        await ctx.send(embed=error_embed, delete_after=30)

        await gumbachi.send(embed=error_embed)

        print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
