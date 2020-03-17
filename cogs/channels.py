import discord
from discord.ext import commands

from classes import Guild
import database as db
from authorization import authorize, is_disabled
from vars import bot


class ChannelCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="welcome")
    async def set_welcome_channel(self, ctx, remove=None):
        """Set welcome channel to the channel the command is called in."""
        authorize(ctx, "channels")
        guild = Guild.get(ctx.guild.id)

        if remove == "remove":
            guild.welcome_channel_id = None
            await ctx.send(f"Success! There is no longer a welcome channel")
        else:
            guild.welcome_channel_id = ctx.channel.id
            await ctx.send(f"Success! {ctx.channel.mention} will now be the channel for greeting people")

        db.update_prefs(guild)  # update preferences

    @commands.command(name="enable")
    async def enable_channel(self, ctx, fill=None):
        """Enable a single channel or all channels."""
        authorize(ctx, "channels")
        guild = Guild.get(ctx.guild.id)

        # enable all channels
        if fill == "all":
            guild.disabled_channel_ids.clear()  # empty list of disabled channels
            await ctx.send(f"All text channels are now enabled!")

        # enable a single channel
        else:
            if ctx.channel.id in guild.disabled_channel_ids:
                guild.disabled_channel_ids.discard(ctx.channel.id)
                await ctx.send(f"channel is now enabled!")
            else:
                await ctx.send(f"channel is already enabled")

        db.update_prefs(guild)

    @commands.command(name="disable")
    async def disable_channel(self, ctx, fill=None):
        """Disable a single channel or all channels."""
        authorize(ctx, "channels")
        guild = Guild.get(ctx.guild.id)

        # disable all channels
        if fill == 'all':
            await ctx.message.delete()
            guild.disabled_channel_ids = {
                channel.id for channel in ctx.guild.text_channels}
            await ctx.send(f"Okay😞 all text channels are now disabled",
                           delete_after=3)

        # disabled a select channel
        else:
            await ctx.message.delete()
            guild.disabled_channel_ids.add(ctx.channel.id)
            # channel has been disabled
            await ctx.send(
                f"Okay😞 {ctx.channel.mention} is now disabled and the party has ended",
                delete_after=3)

        db.update_prefs(guild)  # update database

    @commands.command(name="status")
    async def check_channel_status(self, ctx):
        """Check if a channel is disabled or enabled"""
        guild = Guild.get(ctx.guild.id)

        # returns status of channel
        if ctx.channel in guild.disabled_channels:
            await ctx.message.delete()  # delete command if in disabled channel
            return await ctx.send(f"#{ctx.channel.mention} is disabled.", delete_after=3)
        else:
            await ctx.send(f"{ctx.channel.mention} is enabled")

    @commands.command("channels", aliases=["data"])
    async def channel_data(self, ctx):
        """Displays a list of channels that are enabled and disabled"""
        guild = Guild.get(ctx.guild.id)

        channel_embed = discord.Embed(title=guild.name)

        # add if welcome channel
        if guild.welcome_channel:
            channel_embed.add_field(
                name="Welcome Channel", value=guild.welcome_channel.mention, inline=False)

        if guild.disabled_channels:
            channel_embed.add_field(name="Disabled Channels",
                                    value="\n".join(str(channel)
                                                    for channel in guild.disabled_channels))

        if guild.enabled_channels:
            channel_embed.add_field(name="Enabled Channels",
                                    value="\n".join(channel.mention
                                                    for channel in guild.enabled_channels))

        # check if channel is disabled to choose where to send
        if is_disabled(ctx.channel):
            await ctx.message.delete()
            await ctx.author.send(embed=channel_embed)
        else:
            await ctx.send(embed=channel_embed)


def setup(bot):
    bot.add_cog(ChannelCommands(bot))
