import sys
import traceback

import discord
from discord.ext import commands

import common.cfg as cfg
import common.database as db


class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command."""
        gumbachi = cfg.bot.get_user(128595549975871488)
        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, 'original', error)

        # ignore non-commands
        if isinstance(error, commands.CommandNotFound):
            return

        # General command error (should go last)
        if isinstance(error, commands.CommandError):
            embed = discord.Embed(title=str(error), color=discord.Color.red())
            return await ctx.send(embed=embed)

        # 403 Error
        if isinstance(error, discord.Forbidden):
            # Missing Access
            if error.code == 50001:
                embed = discord.Embed(
                    title="Missing Access",
                    description="The bot is not able to access the channel\nPlease ensure the bot has the correct permissions",
                    color=discord.Color.red()
                )
            # Missing Permissions
            elif error.code == 50013:
                embed = discord.Embed(
                    title="Bot Missing Permissions",
                    description="The bot is missing permissions\nPlease ensure the bot has its required permissions",
                    color=discord.Color.red()
                )

            return await ctx.send(embed=embed)

        # Unusual error to be fixed
        error_embed = discord.Embed(
            title=f'Your command: {ctx.message.content}',
            description=f"{ctx.guild.id}: {error}",
            color=discord.Colour.red()
        )
        await ctx.send(embed=error_embed)  # send to user
        await gumbachi.send(embed=error_embed)  # send to me

        print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
