import discord
from discord.ext import commands

import database as db
from authorization import MissingGuild, is_disabled
from classes import Guild
from utils import rgb_to_hex
from vars import bot, emoji_dict


class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="guildinfo")
    async def show_guild_info(self, ctx, id=None):
        """Shows guild info in an embed."""
        id = ctx.guild.id if not id else id
        guild = Guild.get(int(id))
        embed = discord.Embed(title=guild.name, description=str(guild))
        await ctx.send(embed=embed)

    @commands.command(name="colorinfo")
    async def show_all_color_info(self, ctx, id=None):
        """Shows the info of all colors in a guild"""
        id = ctx.guild.id if not id else id
        guild = Guild.get(int(id))
        cinfo = "\n".join([str(color) for color in guild.colors])
        embed = discord.Embed(title=guild.name, description=cinfo)
        await ctx.send(embed=embed)

    @commands.command(name="themeinfo")
    async def show_all_theme_info(self, ctx, id=None):
        """Shows the info of all colors in a guild"""
        id = ctx.guild.id if not id else id
        guild = Guild.get(int(id))
        cinfo = "\n".join([str(theme) for theme in guild.themes])
        embed = discord.Embed(title=guild.name, description=cinfo)
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


def setup(bot):
    bot.add_cog(UtilityCommands(bot))
