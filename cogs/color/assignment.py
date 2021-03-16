"""Handles all color assignment and roles."""

import random
from itertools import cycle, islice, repeat

import discord
from discord.ext import commands
from discord.ext.commands import CommandError

import common.cfg as cfg
import common.database as db
import common.utils as utils


class ColorAssignment(commands.Cog):
    """Handles commands and listeners related to displaying colors"""

    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        """Disable all commands in cog if heavy command is running."""
        if ctx.guild.id in cfg.heavy_command_active:
            raise CommandError("A command is running, please wait")
        return True

    @staticmethod
    async def color(member, color):
        """Colors a guild member"""
        guild = member.guild
        # Apply already created role
        role = guild.get_role(color["role"])
        try:
            await member.add_roles(role)
        except AttributeError:
            # Role was not found
            # create and apply new role
            role = await ColorAssignment.create_role(guild, color)
            await member.add_roles(role)

    @staticmethod
    async def uncolor(member, color):
        """Removes the color role if a user has one."""
        # do nothing if there is no associated role
        if not color["role"]:
            return

        role = member.guild.get_role(color["role"])
        await member.remove_roles(role)

    @staticmethod
    async def create_role(guild, color):
        """Create a role and update database."""
        role = await guild.create_role(
            name=color["name"],
            color=utils.discord_color(color)
        )
        db.guilds.update_one(
            {"_id": guild.id, "colors.name": color["name"]},
            {"$set": {"colors.$.role": role.id}}
        )
        return role

    ################ COMMANDS #################

    @commands.command(name="color", aliases=["colour", "cu"])
    @commands.has_guild_permissions(manage_roles=True)
    async def color_user(self, ctx, member: discord.Member, *, cstring=""):
        """Color a specified user a specified color."""

        colors = db.get(ctx.guild.id, "colors")
        ucolor = utils.find_user_color(member, colors)

        if not colors:
            raise CommandError("There are no active colors")

        # to eliminate random coloring the same color
        if len(colors) > 1 and not cstring:
            exclusive_colors = [color for color in colors if color != ucolor]
            color = utils.color_lookup(cstring, exclusive_colors)
        else:
            color = utils.color_lookup(cstring, colors)

        if not color:
            raise CommandError("Color Not Found")

        if color == ucolor:
            raise CommandError(f"{member.name} already has that color")

        # attempt to uncolor and then color user
        if ucolor:
            await self.uncolor(member, ucolor)
        await self.color(member, color)

        embed = discord.Embed(
            title=f"{member.name} is {color['name']}",
            color=utils.discord_color(color)
        )
        await ctx.send(embed=embed)

    @commands.command(name="colorme", aliases=["colourme", "cm", "me"])
    async def colorme(self, ctx, *, cstring=""):
        """Display an image of equipped colors."""
        await ctx.invoke(
            self.bot.get_command("color"),
            member=ctx.author,
            cstring=cstring
        )

    @commands.command(name="uncolorme", aliases=["uncolourme", "unme", "ucm"])
    async def uncolorme(self, ctx):
        """Display an image of equipped colors."""
        colors = db.get(ctx.guild.id, "colors")
        ucolor = utils.find_user_color(ctx.author, colors)

        # remove color
        if ucolor:
            await self.uncolor(ctx.author, ucolor)
            response = "You have been uncolored"
        else:
            response = "You don't have a color"

        await ctx.send(embed=discord.Embed(title=response))

    @commands.command(name="splash")
    @commands.has_guild_permissions(manage_roles=True)
    async def color_server(self, ctx, *, color: utils.ColorConverter = None):
        """Gather all of the uncolored users and assigns them a color"""

        colors = db.get(ctx.guild.id, "colors")

        if not colors:
            raise CommandError("There are no active colors")

        cfg.heavy_command_active.add(ctx.guild.id)  # begin heavy command

        # get uncolored members
        uncolored = (member for member in ctx.guild.members
                     if not utils.find_user_color(member, colors))

        msg = await ctx.send(embed=discord.Embed(title="Coloring everyone(may take a while)..."))

        # color generator for splashing
        if not color:
            color_cycle = islice(
                cycle(colors),
                random.randint(0, len(colors)-1),
                None)
        else:
            color_cycle = repeat(color)

        color_memory = {}  # remember roles assigned during command

        # loop and color people
        colored_members = 0
        for member in uncolored:
            color = next(color_cycle)

            # Create role and add it to db instead of in color
            # This is to avoid more db calls than necessary to check a colors existence
            if not color["role"]:
                color["role"] = color_memory.get(color["name"], None)
                if not color["role"]:
                    role = await self.create_role(ctx.guild, color)
                    color_memory[color["name"]] = role.id
                    color["role"] = role.id

            await self.color(member, color)
            colored_members += 1

        cfg.heavy_command_active.discard(ctx.guild.id)

        await msg.edit(embed=discord.Embed(title=f"Colored {colored_members} members!",
                                           color=discord.Color.green()))

    @commands.command(name="unsplash")
    @commands.has_guild_permissions(manage_roles=True)
    async def uncolor_server(self, ctx):
        """Remove all colors but not delete them."""

        colors = db.get(ctx.guild.id, "colors")
        cfg.heavy_command_active.add(ctx.guild.id)  # begin heavy command

        for color in colors:
            if color["role"]:
                role = ctx.guild.get_role(color["role"])
                await role.delete()

        cfg.heavy_command_active.discard(ctx.guild.id)

        await ctx.send(embed=discord.Embed(title="Everyone has been uncolored",
                                           color=discord.Color.green()))

    ############# EVENT LISTENERS #############

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Welcome and attempt to randomly color a new user."""

        # get required data
        wc, colors = db.get_many(member.guild.id, "wc", "colors")

        # do nothing if no welcome channel
        if not wc:
            return
        welcome_channel = member.guild.get_channel(wc)

        if colors:
            color = random.choice(colors)
            await self.color(member, color)
            accent = utils.discord_color(color)
        else:
            accent = discord.Colour.blurple()

        # generate and send weclome embed message
        embed = discord.Embed(
            title=f"{member.name} has joined the server!",
            description=f"Please give {member.mention} a warm welcome!",
            color=accent)
        embed.set_thumbnail(url=member.avatar_url)

        await welcome_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Sends a goodbye message when a member leaves the server."""

        wc, colors = db.get_many(member.guild.id, "wc", "colors")
        ucolor = utils.find_user_color(member, colors)

        # do nothing if no welcome channel
        if not wc:
            return
        welcome_channel = member.guild.get_channel(wc)

        # generate and send goodbye message
        embed = discord.Embed(title=f"{member.name} has left the server!",
                              description="They won't be missed",
                              color=discord.Color.red())
        embed.set_thumbnail(url=member.avatar_url)
        await welcome_channel.send(embed=embed)

        # remove member and update db
        if ucolor:
            members = ucolor["members"]
            members.remove(member.id)
            db.guilds.update_one(
                {"_id": member.guild.id, "colors.name": ucolor["name"]},
                {"$set": {"colors.$.members": members}}
            )

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Updates color info if a users color role is manually removed"""
        # check if any roles changed
        if before.roles == after.roles:
            return

        # convert roles to set for comparison
        roles_before = set(before.roles)
        roles_after = set(after.roles)

        # find difference between sets
        removed_roles = roles_before - roles_after
        added_roles = roles_after - roles_before

        # Role removed
        for role in removed_roles:
            db.guilds.update_one(
                {"_id": after.guild.id, "colors.role": role.id},
                {"$pull": {"colors.$.members": after.id}}
            )

            # clear role if empty
            if not role.members:
                try:
                    await role.delete()
                except discord.errors.NotFound:
                    pass

        # Role added
        for role in added_roles:
            db.guilds.update_one(
                {"_id": after.guild.id, "colors.role": role.id},
                {"$push": {"colors.$.members": after.id}}
            )


def setup(bot):
    bot.add_cog(ColorAssignment(bot))
