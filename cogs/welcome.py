"""Holds commands and listeners related to 
someone joining or the bot joining a server.
"""
import random
import common.database as db
from discord.ext import commands


class WelcomeCommands(commands.Cog):
    """Handles all commands and listeners related to people joining and leaving"""

    def __init__(self, bot):
        self.bot = bot

    # TODO Make this a toggle no args
    @commands.command(name="welcome")
    @commands.has_guild_permissions(manage_channels=True)  # check permissions
    async def set_welcome_channel(self, ctx, *, operation=None):
        """Sets a welcome channel"""
        # choose to remove value or update
        value = None if operation == "off" else ctx.channel.id

        # update db and respond
        db.update_guild(ctx.guild.id, {"welcome_channel": value})
        await ctx.send(f"{ctx.channel.mention} is set as the welcoming channel")

    @commands.Cog.listener()
    async def on_guild_join(guild):
        """Create new object and update database when the bot joins a guild."""
        print(f"ADDED TO {guild.name}:{guild.id}")
        db.add_blank_guild(guild.id)  # Update or add data to db

    @commands.Cog.listener()
    async def on_guild_remove(guild):
        """Delete guild from database if bot is kicked/removed"""
        print(f"REMOVED FROM {guild.name}")
        db.guildcoll.delete_one({"_id": id})

    @commands.Cog.listener()
    async def on_guild_channel_delete(channel):
        """Update database if welcome channel is deleted"""
        db.guildcoll.update_one(
            {"_id": channel.guild.id, "welcome_channel": channel.id},
            {"$set": {"welcome_channel": None}}
        )

    # @commands.Cog.listener
    # async def on_member_join(member):
    #     """Sends a welcome message and attempts to randomly color a user when a
    #     member joins a server the bot is in"""

    #     # get required data
    #     welcome_channel, colors = db.get(
    #         member.guild.id, "welcome_channel", "colors")

    #     # check if there is welcome channel
    #     if not welcome_channel:
    #         return

    #     if colors:
    #         color = random.choice(colors)
    #         # make sure embed can be sent with or without colors
    #     if guild.colors:
    #         color = random.choice(guild.colors)  # get random color
    #         await color_user(guild, member, color)
    #         accent = discord.Color.from_rgb(*color.rgb)  # discord format
    #     else:
    #         color = None
    #         accent = discord.Color.green()

    #     # generate and send weclome embed message
    #     embed = discord.Embed(
    #         title=f"{member.name} has joined the server!",
    #         description=f"Please give {member.mention} a warm welcome!",
    #         color=accent)
    #     embed.set_thumbnail(url=member.avatar_url)

    #     await guild.welcome_channel.send(embed=embed)

    #     if color:
    #         db.update_prefs(guild)


# @bot.event
# async def on_member_remove(member):
#     """Sends a goodbye message when a member leaves a server the bot is in"""
#     guild = Guild.get(member.guild.id)
#     guild.erase_user(member.id)

#     # check if welcome channel or guild exists
#     if not guild.welcome_channel:
#         return

#     # generate and send goodbye message
#     embed = discord.Embed(title=f"{member.name} has left the server!",
#                           description="They won't be missed",
#                           color=discord.Color.red())
#     embed.set_thumbnail(url=member.avatar_url)

#     await guild.welcome_channel.send(embed=embed)
#     db.update_prefs(guild)


def setup(bot):
    bot.add_cog(WelcomeCommands(bot))
