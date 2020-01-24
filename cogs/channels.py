import discord
from discord.ext import commands
from functions import update_prefs
from vars import bot
from classes import Guild

class ChannelCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #set welcome channel
    @commands.command(name="welcome")
    async def set_welcome_channel(self, ctx, remove=None):
        #check permissions
        if not ctx.author.guild_permissions.manage_channels:
            return await ctx.send("You need `manage channels` permission to use this command")

        guild = Guild.get_guild(ctx.guild.id)
        guild.welcome_channel = ctx.channel.id

        if remove == "remove":
            guild.welcome_channel = None
            await ctx.send(f"Success! There is no longer a welcome channel")
        else:
            await ctx.send(f"Success! {ctx.channel.mention} will now be the channel for greeting people")

        await update_prefs([guild])#update preferences

    #enables a channel or all channels for command use
    @commands.command(name="enable")
    async def enable_channel(self, ctx, fill=None):
        guild = Guild.get_guild(ctx.guild.id)

        #check permissions
        if not ctx.author.guild_permissions.manage_channels:
            return await ctx.send("You need `manage channels` permission to use this command\nThis message will self-destruct shortly", delete_after=7)

        #go through all channels and enable all of them
        if fill == 'all':
            guild.disabled_channels.clear() #empty list of disabled channels
            await ctx.send(f"All text channels are now enabled!")
        else:
            if ctx.channel.id in guild.disabled_channels:
                guild.disabled_channels.remove(ctx.channel.id)
                await ctx.send(f"channel is now enabled!")
            else:
                await ctx.send(f"channel is already enabled")

        await update_prefs([guild]) #update database

    #disable one channel or all channels
    @commands.command(name="disable")
    async def disable_channel(self, ctx, fill=None):
        #check permissions
        if not ctx.author.guild_permissions.manage_channels:
            return await ctx.send("You need `manage channels` permission to use this command")

        guild = Guild.get_guild(ctx.guild.id)

        #disable all channels
        if fill == 'all':
            for channel in ctx.guild.text_channels:
                if channel.id not in guild.disabled_channels:
                    guild.disabled_channels = [channel.id for channel in ctx.guild.text_channels] #list comp of all channel ids
            await ctx.send(f"Okay😞 all text channels are now disabled.\nThis message will self-destruct shortly", delete_after=7)

        #disabled a select channel
        else:
            if ctx.channel.id not in guild.disabled_channels:
                guild.disabled_channels.append(ctx.channel.id)
                await ctx.send(f"Okay😞 {ctx.channel.mention} is now disabled and the party has ended.\nThis message will self-destruct shortly", delete_after=7) #channel has been disabled
            else:
                await ctx.send(f"{ctx.channel.mention} is already disabled.\nThis message will self-destruct shortly", delete_after=7)#channel was already disabled

        await update_prefs([guild])#update database

    #check status of a channel
    @commands.command(name="status")
    async def check_channel_status(self, ctx):
        disabled = Guild.get_guild(ctx.guild.id).disabled_channels

        #returns status of channel
        if ctx.channel.id in disabled:
            await ctx.message.delete() #delete command if in disabled channel
            return await ctx.send(f"#{ctx.channel.mention} is disabled.\nThis message will self-destruct shortly", delete_after=7)
        else:
            return await ctx.send(f"{ctx.channel.mention} is enabled")

def setup(bot):
    bot.add_cog(ChannelCommands(bot))