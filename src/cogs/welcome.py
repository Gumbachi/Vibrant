"""Holds commands and listeners related to 
someone joining or the bot joining a server.
"""
from discord.ext.commands.core import check
import common.database as db
from discord.ext import commands
from common.utils import check_emoji


class WelcomeCommands(commands.Cog):
    """Handles all commands and listeners related to people joining and leaving"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="welcome", aliases=["wc"])
    @commands.has_guild_permissions(manage_channels=True)  # check permissions
    async def set_welcome_channel(self, ctx):
        """Sets or unsets a welcome channel."""
        response = db.guilds.update_one(
            {"_id": ctx.guild.id, "wc": ctx.channel.id},
            {"$set": {"wc": None}}
        )

        # Check for found and changed document
        if response.matched_count == 1:
            return await ctx.send(f"{ctx.channel.mention} is no longer the welcome channel {check_emoji()}")

        # else change it to new channel
        db.guilds.update_one(
            {"_id": ctx.guild.id},
            {"$set": {"wc": ctx.channel.id}}
        )
        await ctx.send(f"{ctx.channel.mention} is set as the welcoming channel {check_emoji()}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Add new guild to database."""
        db.guilds.insert_one(
            {
                "_id": guild.id,
                "prefix": "$",
                "wc": None,
                "colors": [],
                "themes": []
            }
        )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """Delete guild from database if bot is kicked/removed"""
        db.guilds.delete_one({"_id": guild.id})

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Update database if welcome channel is deleted."""
        db.guilds.update_one(
            {"_id": channel.guild.id, "wc": channel.id},
            {"$set": {"wc": None}}
        )


def setup(bot):
    bot.add_cog(WelcomeCommands(bot))
