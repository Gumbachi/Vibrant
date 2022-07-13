"""Handles all color assignment and roles."""

import asyncio
import random
from itertools import cycle, repeat

import discord
from common.database import db
from common.utils import no_colors_embed
from discord import ApplicationContext, Option, slash_command, user_command
from model.color import Color
from model.theme import Theme


class ColorAssignment(discord.Cog):
    """Handles commands and listeners related to displaying colors"""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @user_command(name="Color Random")
    async def randomly_color(self, ctx: ApplicationContext, member: discord.Member):
        """Change color to a random color"""
        colors: list[Color] = db.get_colors()

        if not colors:
            return await ctx.respond(
                "You have no colors. Use the /colors command to manage your colors"
            )

        color = random.choice(colors)

        role = color.get_role(ctx.guild)

        if not role:
            role = await ctx.guild.create_role(
                name=color.name, color=color.to_discord_color()
            )

        await member.add_roles(role)

    @discord.slash_command(name="color")
    async def color_user(
        self,
        ctx: discord.ApplicationContext,
        member: Option(discord.Member, description="The person to be colored"),
        color: Color,
    ):
        """Default command for coloring somebody or yourself."""
        await ctx.respond("TODO")

    @discord.slash_command(name="colorme")
    async def color_user(self, ctx: discord.ApplicationContext, color: Color):
        """Default command for coloring somebody or yourself."""
        # Just call color from here
        await ctx.respond("TODO")

    @staticmethod
    async def old_color(member, color):
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
            name=color["name"], color=utils.discord_color(color)
        )
        db.guilds.update_one(
            {"_id": guild.id, "colors.name": color["name"]},
            {"$set": {"colors.$.role": role.id}},
        )
        return role

    ################ COMMANDS #################

    @slash_command(name="color")
    async def color_user(
        self,
        ctx: ApplicationContext,
        member: Option(discord.Member, "The one to be colored"),
        color: Option(discord.Color, "The color to apply", required=False),
    ):
        """Color somebody."""

        # TODO Get theme for guild
        theme = Theme()

        if theme.empty:
            return await ctx.respond(embed=no_colors_embed())

        if not color:
            newcolor = theme.random_color()

        colors = db.get(ctx.guild.id, "colors")
        ucolor = utils.find_user_color(member, colors)

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
            title=f"{member.name} is {color['name']} {check_emoji()}",
            color=utils.discord_color(color),
        )
        await ctx.send(embed=embed)

    @commands.command(name="colorme", aliases=["colourme", "cm", "me", "cme"])
    async def colorme(self, ctx, *, cstring=""):
        """Display an image of equipped colors."""
        await ctx.invoke(
            self.bot.get_command("color"), member=ctx.author, cstring=cstring
        )

    @commands.command(name="uncolorme", aliases=["uncolourme", "unme", "ucm"])
    async def uncolorme(self, ctx):
        """Display an image of equipped colors."""
        colors = db.get(ctx.guild.id, "colors")
        ucolor = utils.find_user_color(ctx.author, colors)

        # remove color
        if ucolor:
            await self.uncolor(ctx.author, ucolor)
            response = f"You have been uncolored {check_emoji()}"
        else:
            response = "You don't have a color"

        await ctx.send(embed=discord.Embed(title=response))

    @commands.command(name="splash")
    @commands.has_guild_permissions(manage_roles=True)
    async def color_server(self, ctx, *, color: utils.ColorConverter = None):
        """Gather all of the uncolored users and assigns them a color"""

        output_suppressed = ctx.guild.id in cfg.suppress_output
        colors = db.get(ctx.guild.id, "colors")  # Fetch colors

        if not colors:
            raise CommandError("There are no active colors")

        cfg.heavy_command_active.add(ctx.guild.id)  # begin heavy command

        # get uncolored members
        uncolored = [
            member
            for member in ctx.guild.members
            if not utils.find_user_color(member, colors)
        ]

        # Send working message
        if not output_suppressed:
            embed = discord.Embed(title=f"Creating Roles {loading_emoji()}")
            msg = await ctx.send(embed=embed)

        # color generator for splashing
        colors = [color] if color else colors  # One color needed if color arg
        index = random.randrange(len(colors))  # random index in colors
        sliced_colors = colors[index:] + colors[:index]

        # Loop over all colors that will be applied and create roles
        for color in sliced_colors[: len(uncolored)]:
            if not color["role"]:
                role = await self.create_role(ctx.guild, color)
                color["role"] = role.id

        # Send progress update
        if not output_suppressed:
            embed = discord.Embed(
                title=f"Coloring {len(uncolored)} People {loading_emoji()}",
                description=f"This will take around {len(uncolored)} seconds",
            )
            await msg.edit(embed=embed)

        # Loop and color every member sleeping a bit inbetween
        for color, member in zip(cycle(sliced_colors), uncolored):
            await self.color(member, color)
            await asyncio.sleep(1)

        cfg.heavy_command_active.discard(ctx.guild.id)

        # Send success message
        if not output_suppressed:
            embed = discord.Embed(
                title=f"Colored {len(uncolored)} members {check_emoji()}",
                color=discord.Color.green(),
            )
            await msg.edit(embed=embed)

    @commands.command(name="unsplash")
    @commands.has_guild_permissions(manage_roles=True)
    async def uncolor_server(self, ctx):
        """Remove all colors but not delete them."""

        colors = db.get(ctx.guild.id, "colors")
        cfg.heavy_command_active.add(ctx.guild.id)  # begin heavy command

        # Remove every role associated with a color
        for color in colors:
            if color["role"]:
                role = ctx.guild.get_role(color["role"])
                await role.delete()

        cfg.heavy_command_active.discard(ctx.guild.id)  # end heavy cmd

        # Send success message
        if ctx.guild.id not in cfg.suppress_output:
            embed = discord.Embed(
                title=f"Everyone has been uncolored {check_emoji()}",
                color=discord.Color.green(),
            )
            await ctx.send(embed=embed)

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
            color=accent,
        )
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
        embed = discord.Embed(
            title=f"{member.name} has left the server!",
            description="They won't be missed",
            color=discord.Color.red(),
        )
        embed.set_thumbnail(url=member.avatar_url)
        await welcome_channel.send(embed=embed)

        # remove member and update db
        if ucolor:
            members = ucolor["members"]
            members.remove(member.id)
            db.guilds.update_one(
                {"_id": member.guild.id, "colors.name": ucolor["name"]},
                {"$set": {"colors.$.members": members}},
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
            response = db.guilds.update_one(
                {"_id": after.guild.id, "colors.role": role.id},
                {"$pull": {"colors.$.members": after.id}},
            )

            # clear role if empty
            if not role.members and response.matched_count == 1:
                try:
                    await role.delete()
                except discord.errors.NotFound:
                    pass
                except discord.Forbidden:
                    pass

        # Role added
        for role in added_roles:
            db.guilds.update_one(
                {"_id": after.guild.id, "colors.role": role.id},
                {"$push": {"colors.$.members": after.id}},
            )


def setup(bot: discord.Bot):
    bot.add_cog(ColorAssignment(bot))
