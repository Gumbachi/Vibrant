import re
import random
import discord
from discord.ext import commands
from webcolors import hex_to_rgb
from fuzzywuzzy import fuzz, process
from functions import is_disabled, update_prefs, check_hex
from vars import bot, get_prefix, get_help, change_log, get_commands
from classes import Guild, Color

class BaseCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx, arg=None):
        disabled = is_disabled(ctx.channel)
        if disabled:
            await ctx.message.delete()

        p = get_prefix(bot, ctx.message)
        help_dict = get_help(p)
        if not arg:
            recipient = ctx if not disabled else ctx.author
            title = "ColorBOT Help"
            description = f"Table of Contents.\nTo go to another page please use `{p}help <page number>`\nExample `{p}help 1`"
            fields = help_dict[None].items()
        elif arg == '1' or 'setup':
            recipient = ctx.author
            title = "ColorBOT Setup"
            description = "Follow these steps to learn how to use ColorBOT"
            fields = help_dict[1].items()
        elif arg == '2' or 'commands':
            recipient = ctx.author
            title = "ColorBOT Commands"
            description = f"A list of commands the bot has. For more info on a specific command you can use `{p}help <command>`\nExample: `{p}help add`"
            fields = help_dict[2].items()
        elif arg in [command.name for command in bot.commands]:
            recipient = ctx if not disabled else ctx.author
            commands = get_commands(p)
            title = f"{p}{arg}"
            description = f"An in-depth description of the `{p}{arg}` command"
            fields = commands[arg].items()
        else:
            raise Exception(f"Invalid Input. Type `{p}help` for more help")

        #generate embed
        help_embed = discord.Embed(title=title, description=description, color=discord.Colour.blue())
        for k,v in fields:
            help_embed.add_field(name=k, value=v, inline=False)

        if recipient is ctx.author and not disabled:
            await ctx.send("You've got mail!")
        await recipient.send(embed=help_embed)#send to either channel or DM

    #reply howdy to user in channel or in DM
    @commands.command(name='howdy')
    async def howdy(self, ctx):
        if is_disabled(ctx.channel): 
            return await ctx.author.send(f"Howdy, {ctx.message.author.mention}!") #send in dms
        await ctx.send(f"Howdy, {ctx.message.author.mention}!")#send in channel

    #change the server prefix
    @commands.command(name='prefix', aliases=['colorbotprefix'])
    async def change_prefix(self, ctx, new_prefix=None):
        #check permissions
        if not ctx.author.guild_permissions.manage_guild:
            return await ctx.send(f"{ctx.author.mention}, you need `manage server` permissions to use this command")
        
        guild = Guild.get_guild(ctx.guild.id)
        if not new_prefix:
            return await ctx.send(f"Current Prefix: `{guild.prefix}`")
        
        guild.prefix = new_prefix
        await ctx.send(f"New Prefix is `{new_prefix}`")
        await update_prefs([guild])#update database

    #show info about a user
    @commands.command("expose", aliases=['whois'])
    async def expose_user(self, ctx, *name):
        user = " ".join(name)

        #find the right user
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        elif user == "":
            user = ctx.author
        else:
            return await ctx.send("you need to mention a user")

        guild = Guild.get_guild(ctx.guild.id)
        color_role = guild.get_color_role(user)
        rgb = color_role.color if color_role else discord.Color.light_grey() #discord color object

        #generate embed
        expose_embed = discord.Embed(title = f"{user.name}#{user.discriminator}", description = ' ', color = rgb)

        #structure embed
        expose_embed.set_author(name = user.name if user.nick is None else user.nick, icon_url = user.avatar_url)
        expose_embed.add_field(name = "Favorite Color", value = color_role.name if color_role else "None")
        expose_embed.add_field(name = 'Status', value = str(user.status))
        expose_embed.add_field(name = 'Member Since', value = str(user.joined_at)[:10])
        expose_embed.set_thumbnail(url = user.avatar_url)
        expose_embed.set_footer(text = f"ID: {user.id}")

        #send to right location
        if is_disabled(ctx.channel):
            await ctx.message.delete()
            await ctx.author.send(embed=expose_embed)
        else:
            await ctx.send(embed=expose_embed)

    #shows enabled and disabled channels
    @commands.command("channels", aliases=["data"])
    async def channel_data(self, ctx):
        guild = Guild.get_guild(ctx.guild.id)
        
        welcome = "Not set"
        if guild.welcome_channel:
            welcome = bot.get_channel(guild.welcome_channel).name

        disabled, enabled = [], []
        for channel in ctx.guild.text_channels:
            if channel.id in guild.disabled_channels:
                disabled.append(f"`{channel.name}`")
            else:
                enabled.append(f"`{channel.name}`")

        embed = discord.Embed(title=guild.name, description=f"Welcome Channel: `{welcome}`")
        embed.add_field(name="Enabled Channels", value="\n".join(enabled) if enabled else "None")
        embed.add_field(name="Disabled Channels", value="\n".join(disabled) if disabled else "None")

        #check if channel is disabled to choose where to end
        if is_disabled(ctx.channel):    
            await ctx.message.delete()#delete command if channel is disabled
            return await ctx.author.send(embed=embed)
        await ctx.send(embed=embed)

    @commands.command(name="version", aliases=["patchnotes"])
    async def patchnotes(self, ctx, version=None):
        #generate formatted embed to send to user
        latest = "1.9"

        #get correct version
        if version in change_log.keys():
            info = change_log[version]
        else:
            info = change_log[latest]
            version = latest

        #create and add to embed
        patch_embed = discord.Embed(title=f"ColorBOT v{version} Patch Notes",
                                    description=f"Current Version: {latest}\n Versions: {', '.join(change_log.keys())}", 
                                    color=discord.Colour.blue())
        for k,v in info.items():
            patch_embed.add_field(name=k, value=v, inline=False)

        patch_embed.set_thumbnail(url=bot.user.avatar_url)
        return await ctx.send(embed=patch_embed)

    #send a message to gumbachi
    @commands.command(name="report")
    async def report(self, ctx, *msg):
        gumbachi = bot.get_user(128595549975871488)
        report_embed = discord.Embed(title = f"Report from {ctx.author.name} in {ctx.guild.name}",
                                    description = " ".join(msg), 
                                    color = discord.Colour.blue())
        await gumbachi.send(embed = report_embed)
        await ctx.send("Message sent.")

def setup(bot):
    bot.add_cog(BaseCommands(bot))