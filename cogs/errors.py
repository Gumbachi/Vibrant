import sys, traceback
import discord
from discord.ext import commands
from vars import bot, get_prefix

class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # https://gist.github.com/EvieePy/7822af90858ef65012ea500bcecf1612

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""

        print(error)
        print(type(error))

        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound, commands.UserInputError)#ignored errors
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except: pass

        elif isinstance(error, discord.HTTPException) and error.code == 50007:
            return await ctx.send(f"Couldn't DM {ctx.author.mention}. Probably has me blocked")

        elif isinstance(error, discord.errors.Forbidden) and error.code == 50013:
            return await ctx.send(f"I don't have permission to do this. This can be solved by reinviting the bot or making sure the bot has permission to manage roles/messages")

        elif isinstance(ctx.channel, discord.channel.DMChannel):
            return await ctx.send(f"That command must be used in a server channel")

        error_embed = discord.Embed(title=f'Your command: {ctx.message.content}',
                                    description=str(error),
                                    color=discord.Colour.red())
        await ctx.send(embed=error_embed, delete_after=30)

        gumbachi = bot.get_user(128595549975871488)
        await gumbachi.send(embed=error_embed)

        print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))