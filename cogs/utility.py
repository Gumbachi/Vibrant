import discord
from discord.ext import commands

from classes import Guild
from utils import rgb_to_hex
import database as db
from authorization import is_disabled, MissingGuild
from vars import bot, emoji_dict


class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="update")
    async def update_mongo(self, ctx):
        """Update all documents in database"""
        if ctx.author.id != 128595549975871488:
            return

        db.update_prefs(*list(Guild._cache.values()))
        await ctx.send("update complete")

    @commands.command(name="dstats")
    async def devstats(self, ctx):
        print(len(Guild._cache))
        print(Guild._cache)

    @commands.command(name="guildinfo")
    async def show_guild_info(self, ctx, id=None):
        """Shows guild info in an embed and in terminal"""
        if not id:
            id = ctx.guild.id
        guild = Guild.get(int(id))
        embed = discord.Embed(title="Guild info", description=repr(guild))
        await ctx.send(embed=embed)

    @commands.command(name="colorinfo")
    async def show_all_color_info(self, ctx):
        """Shows the info of all colors in a guild"""
        guild = Guild.get(ctx.guild.id)
        s = "Colors\n"
        for color in guild.colors:
            s += f"    {repr(color)}\n"
        embed = discord.Embed(title="Colors info", description=s)
        await ctx.send(embed=embed)

    @commands.command(name='purge')
    async def delete_messages(self, ctx, amount):
        verified_ids = [
            224506294801793025,
            244574519027564544,
            187273639874396160,
            128595549975871488
        ]
        if ctx.author.id in verified_ids:
            await ctx.channel.purge(limit=int(amount)+1)
            await ctx.send(f"purged {amount} messages", delete_after=2)

    @commands.command(name="repeat", aliases=["print", "write"])
    async def repeat(self, ctx, *, msg):
        await ctx.send(msg)

    @commands.command(name="check")
    async def is_visible(self, ctx, id=None):
        if ctx.author.id != 128595549975871488:
            return

        if not id:
            id = ctx.guild.id
        id = int(id)

        dguild = bot.get_guild(id)
        name = dguild.name if dguild else "None"

        embed = discord.Embed(
            title=name, description="Checks info for a specific server")

        if bot.get_guild(id):
            embed.add_field(name="Visible", value=emoji_dict["checkmark"])
        else:
            embed.add_field(name="Visible", value=emoji_dict["crossmark"])

        try:
            guild = Guild.get(id)
            embed.add_field(name="Memory", value=emoji_dict["checkmark"])
        except MissingGuild:
            embed.add_field(name="Memory", value=emoji_dict["crossmark"])
            return await ctx.send(embed=embed)

        for member in guild.members:
            if member.id == bot.user.id:
                botmember = member
                break

        botperms = botmember.guild_permissions
        perms = (f"Manage Roles: {emoji_dict['checkmark'] if botperms.manage_roles else emoji_dict['crossmark']}\n"
                 f"Send Messages: {emoji_dict['checkmark'] if botperms.send_messages else emoji_dict['crossmark']}\n"
                 f"Manage Messages: {emoji_dict['checkmark'] if botperms.manage_messages else emoji_dict['crossmark']}\n"
                 f"Attach Files: {emoji_dict['checkmark'] if botperms.attach_files else emoji_dict['crossmark']}")

        embed.add_field(name="Permissions", value=perms)

        stats = (f"Members: {len(guild.members)}\n"
                 f"Colors: {len(guild.colors)}\n"
                 f"Themes: {len(guild.themes)}\n")
        embed.add_field(name="Stats", value=stats)

        await ctx.send(embed=embed)

    @commands.command(name="deletelocal")
    async def remove_guild(self, ctx, id):
        if ctx.author.id != 128595549975871488:
            return

        guild = Guild._cache.pop(int(id), "None")
        await ctx.send(f"Forcibly removed {str(guild)}")

    @commands.command(name="len")
    async def count_local(self, ctx):
        if ctx.author.id != 128595549975871488:
            return
        await ctx.send(len(Guild._cache))

    @commands.command(name="testrole")
    async def make_test_role(self, ctx):
        await ctx.send("Making role")
        role = await ctx.guild.create_role(
            name="Testing Role", color=discord.Color.green())
        await ctx.author.add_roles(role)


def setup(bot):
    bot.add_cog(UtilityCommands(bot))
