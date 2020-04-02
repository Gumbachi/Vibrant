import discord
from discord.ext import commands

from classes import Guild
from functions import rgb_to_hex
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

        db.update_prefs(*list(Guild._guilds.values()))
        await ctx.send("update complete")

    @commands.command(name="correct_members")
    async def fix_member_roles(self, ctx):
        if ctx.author.id != 128595549975871488:
            return

        for guild in Guild._guilds.values():
            for color in guild.colors:
                if color.role_id:
                    try:
                        role = guild.discord_guild.get_role(color.role_id)
                        color.member_ids = {
                            member.id for member in role.members}
                    except:
                        print("broke")

                else:
                    color.member_ids = set()
            db.update_prefs(guild)
        print("Finished")

    @commands.command(name="trim_members")
    async def purge_members(self, ctx, *, id=None):
        if ctx.author.id != 128595549975871488:
            return

        if not id:
            for guild in Guild._guilds.values():
                all_members = set()
                verified_members = {
                    member.id for member in guild.discord_guild.members}
                for color in guild.colors:
                    color.member_ids &= verified_members
                    color.member_ids -= all_members
                    all_members |= color.member_ids
        else:
            guild = Guild.get(int(id))
            all_members = set()
            verified_members = {
                member.id for member in guild.discord_guild.members}
            for color in guild.colors:
                if not color.member_ids:
                    continue
                color.member_ids &= verified_members
                color.member_ids -= all_members
                all_members |= color.member_ids
            db.update_prefs(guild)
        await ctx.send("Done")

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

    @commands.command(name="botstats")
    async def count_guilds(self, ctx):
        users = 0
        colors = 0
        themes = 0
        exceptions = 0
        for guild in Guild._guilds.values():
            try:
                users += len(guild.discord_guild.members)
                colors += len(guild.colors)
                themes += len(guild.themes)
            except:
                exceptions += 1
        stat_embed = discord.Embed(
            title="Stats",
            description=f"Servers: {len(bot.guilds)}\nUsers: {users}\nColors: {colors}\nThemes: {themes}\nExceptions: {exceptions}")
        await ctx.send(embed=stat_embed)

    @commands.command(name="announce")
    async def send_to_all_guilds(self, ctx, *message):
        if ctx.author.id != 128595549975871488:
            return
        #announce_embed = discord.Embed(title="ColorBOT Announcement", description=" ".join(message))
        # unfinished

    @commands.command(name="deleteguild")
    async def remove_guild(self, ctx, id):
        if ctx.author.id != 128595549975871488:
            return

        guild = Guild._guilds.pop(int(id), "None")
        print(f"Forcibly removed {guild.name}")


def setup(bot):
    bot.add_cog(UtilityCommands(bot))
