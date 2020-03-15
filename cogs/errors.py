import sys
import traceback
import discord
from discord.ext import commands
from vars import bot, get_prefix
import authorization as auth
from classes import Guild


class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command."""

        print(f"ERROR TYPE: {type(error)}")
        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound)  # ignored errors
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        elif isinstance(error, auth.HeavyCommandActive):
            return await ctx.send(f"**{error}** is running right now. Please wait for it to finish.")

        elif isinstance(error, auth.MissingPermissions):
            return await ctx.send(f"You need `{error}` permissions to use that command.")

        elif isinstance(error, auth.ChannelDisabled):
            try:
                await ctx.message.delete()
                guild = Guild.get(ctx.guild.id)
                embed = discord.Embed(title=f"{ctx.channel.name} is disabled",
                                      description=(f"Enabled channels for {guild.name}:\n"
                                                   f"{', '.join([channel.mention for channel in guild.enabled_channels])}"))
                return await ctx.author.send(embed=embed)
            except:
                return

        elif isinstance(error, auth.InvalidHexcode):
            embed = discord.Embed(
                title="Invalid Hex Code",
                description=(f"{error} is not a valid color "
                             "[hex code](https://www.google.com/search?q=color+picker)"))
            return await ctx.send(embed=embed)

        elif isinstance(error, auth.NoAvailableColors):
            embed = discord.Embed(
                title="No Available Colors",
                description="Solution: You need to add some colors or load a preset. You can learn how with the help command")
            return await ctx.send(embed=embed)

        elif isinstance(error, discord.HTTPException) and error.code == 50007:
            return await ctx.send(f"Couldn't DM {ctx.author.mention}. Probably has me blocked")

        elif isinstance(error, discord.errors.Forbidden) and error.code == 50013:
            return await ctx.send(
                f"I don't have permission to do this. This can be solved by reinviting the bot or making sure the bot has permission to manage roles/messages")

        elif isinstance(ctx.channel, discord.channel.DMChannel):
            return await ctx.send(f"**{ctx.command}** must be used in a server channel")

        error_embed = discord.Embed(title=f'Your command: {ctx.message.content}',
                                    description=str(error),
                                    color=discord.Colour.red())
        await ctx.send(embed=error_embed, delete_after=30)

        gumbachi = bot.get_user(128595549975871488)
        await gumbachi.send(embed=error_embed)

        print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
