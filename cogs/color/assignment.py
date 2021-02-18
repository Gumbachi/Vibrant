import common.database as db
import discord
from common.utils import ColorConverter as Color
from common.utils import color_lookup, discord_color
from discord.ext import commands


class ColorAssignment(commands.Cog):
    """Handles commands and listeners related to displaying colors"""

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def color(member, color):
        """Colors a guild member"""
        guild = member.guild
        # Apply already created role
        if color["role"]:
            role = guild.get_role(color["role"])
            await member.add_roles(role)

        # create and apply role
        else:
            role = await guild.create_role(
                name=color["name"],
                color=discord_color(color)
            )
            await member.add_roles(role)

        db.update_member(member.id, {str(member.guild.id): role.id})
        db.guildcoll.update_one(
            {"_id": member.guild.id, "colors": color},
            {"$set": {"colors.$.role": role.id}}
        )

    @staticmethod
    async def uncolor(member, role_id):
        """Removes the color role if a user has one."""
        role = member.guild.get_role(role_id)
        if role:
            await member.remove_roles(role)
        db.update_member(member.id, {str(member.guild.id): None})

    @commands.command(name="colorme", aliases=["colourme", "me"])
    async def colorme(self, ctx, *, color=""):
        """Display an image of equipped colors."""
        colors = db.get(ctx.guild.id, "colors")
        color = color_lookup(color, colors)  # find right color

        member = db.find_member(ctx.author.id)

        # remove color if necessary
        role_id = member.get(str(ctx.guild.id), None)
        if role_id:
            await ColorAssignment.uncolor(ctx, role_id)

        # apply color
        await ColorAssignment.color(ctx.author, color)

        embed = discord.Embed(
            title=f"You have been painted {color['name']}",
            color=discord_color(color))
        await ctx.send(embed=embed)

    @ commands.command(name="uncolorme", aliases=["uncolourme", "unme"])
    async def uncolorme(self, ctx):
        """Display an image of equipped colors."""
        colors = db.get(ctx.guild.id, "colors")

        # Switch colors
        await ColorAssignment.uncolor(ctx.author, colors)

        embed = discord.Embed(title=f"You have been uncolored")
        await ctx.send(embed=embed)

    # @commands.Cog.listener()
    # async def on_member_update(before, after):
    #     """updates color info if a users color role is manually removed"""
    #     # check if any roles changed
    #     if before.roles == after.roles:
    #         return

    #     # convert roles to set for comparison
    #     roles_before = set(before.roles)
    #     roles_after = set(after.roles)

    #     # find difference between sets
    #     removed_roles = roles_before - roles_after
    #     added_roles = roles_after - roles_before

    #     for role in removed_roles:
    #         db.coll.update(
    #             {"_id": after.guild.id}
    #         )

    #     # role removed
    #     if removed_roles:
    #         for role in removed_roles:
    #             color = guild.get_color("role_id", role.id)
    #             if color:
    #                 color.member_ids.discard(before.id)
    #                 if not color.member_ids:
    #                     try:
    #                         await role.delete()
    #                     except discord.errors.NotFound:
    #                         pass

    #     # role added
    #     if added_roles:
    #         for role in added_roles:
    #             color = guild.get_color("role_id", role.id)
    #             if color:
    #                 color.member_ids.add(before.id)


# @bot.event
# async def on_guild_role_delete(role):
#     """Removes a role from the Guild object if user deletes it"""
#     guild = Guild.get(role.guild.id)

#     # sets color role id to none if it is deleted
#     color = guild.get_color("role_id", role.id)
#     if color:
#         color.role_id = None
#         if not guild.heavy_command_active:
#             db.update_prefs(guild)  # update MongoDB


def setup(bot):
    bot.add_cog(ColorAssignment(bot))
