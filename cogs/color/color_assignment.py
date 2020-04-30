import random
from random import randint
from itertools import islice, cycle, repeat

import discord
from discord.ext import commands

import database as db
from classes import Guild, Color
from authorization import authorize, MissingPermissions, NotFoundError
from vars import bot, emoji_dict
from utils import check_hex


class ColorAssignment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="color", aliases=["colour", "cu"])
    async def color(self, ctx, user, *, color_query=""):
        """Color a specified user a specified color.

        Args:
            user (str): The name of the user or a mention
            color (tuple of str): The name of the desired color
        """
        authorize(ctx, "disabled", "roles", "colors", user_query=(user, 90))
        guild = Guild.get(ctx.guild.id)

        user = guild.find_user(user, ctx.message)

        # find color
        if color_query:
            color = guild.find_color(color_query)
            if not color:
                try:
                    authorize(ctx, "roles")
                    return await add_color_UX(ctx, color_query, user)
                except MissingPermissions:
                    raise NotFoundError()
        else:
            color = random.choice(guild.colors)

        await color_user(guild, user, color)
        await ctx.send(f"Gave **{user.name}** the **{color.name}** role")
        db.update_prefs(guild)

    @commands.command(name="colorme", aliases=["me", "colourme"])
    async def colorme(self, ctx, *, color_query=""):
        """Assign a Color to the author of the command."""
        authorize(ctx, "disabled", "colors")

        guild = Guild.get(ctx.guild.id)

        if color_query:
            color = guild.find_color(color_query)
            if not color:
                try:
                    authorize(ctx, "roles")
                    return await add_color_UX(ctx, color_query, ctx.author)
                except MissingPermissions:
                    raise NotFoundError()
        else:
            color = random.choice(guild.colors)

        await color_user(guild, ctx.author, color)
        await ctx.send(f"You are now colored **{color.name}**")
        db.update_prefs(guild)

    @commands.command(name="uncolorme", aliases=["uncolourme", "ucm"])
    async def uncolor_me(self, ctx):
        """Remove an existing Color from the author"""
        authorize(ctx, "disabled", has_color=ctx.author)

        guild = Guild.get(ctx.guild.id)
        role = guild.get_color_role(ctx.author)

        color = guild.get_color("role_id", role.id)

        # remove roles and send success message
        await ctx.author.remove_roles(role)
        color.member_ids.discard(ctx.author.id)
        await ctx.send(f"You are no longer colored **{role.name}**")
        db.update_prefs(guild)

    @commands.command(name="splash")
    async def color_server(self, ctx, color=None):
        """Gather all of the uncolored users and assigns them a color.

        Args:
            color (str): An optional arg for coloring everyone a single color
            trace (bool): Whether or not the function should print anything
        """
        authorize(ctx, "disabled", "roles", "colors", "heavy")

        guild = Guild.get(ctx.guild.id)

        # get specific color
        if color:
            authorize(ctx, color_query=(color, 90))
            color = guild.find_color(color)

        guild.heavy_command_active = ctx.command.name

        # get uncolored members
        uncolored = (member for member in ctx.guild.members
                     if not guild.get_color_role(member))

        await ctx.send("Coloring everyone...")

        # color generator for splashing
        if not color:
            color_cycle = islice(cycle(guild.colors),
                                 randint(0, len(guild.colors)-1),
                                 None)
        else:
            color_cycle = repeat(color)

        # loop through and color members
        async with ctx.channel.typing():
            for member in uncolored:
                await color_user(guild, member, next(color_cycle))

        guild.heavy_command_active = None

        await ctx.send("Everyone visible has been colored!")
        db.update_prefs(guild)

    @commands.command(name="unsplash")
    async def uncolor_server(self, ctx):
        """Gather all of the uncolored users and assigns them a color.

        Args:
            color (str): An optional arg for coloring everyone a single color
            trace (bool): Whether or not the function should print anything
        """
        authorize(ctx, "disabled", "roles", "heavy")

        guild = Guild.get(ctx.guild.id)

        await ctx.send("Uncoloring everyone...")
        guild.heavy_command_active = ctx.command.name

        # loop through and color members
        async with ctx.channel.typing():
            for color in guild.colors:
                # delete role
                if color.role:
                    await color.role.delete()

                color.member_ids.clear()  # Clear members from color

        guild.heavy_command_active = None
        await ctx.send("Everyone has been uncolored!")

        db.update_prefs(guild)

    @commands.Cog.listener()
    async def on_message(self, message):
        # handles message verification if user is adding a color via reaction
        if check_hex(message.content):
            guild = Guild.get(message.guild.id)

            # listen for hexcode
            if message.author.id == guild.waiting_on_hexcode.get("id"):
                ctx = await bot.get_context(message)
                user = guild.waiting_on_hexcode.get("user")
                color = await ctx.invoke(bot.get_command("add"),
                                         hexcode=message.content,
                                         name=guild.waiting_on_hexcode.get("color", "No Name"))
                await color_user(guild, user, color)
                await ctx.send(f"{user.name} has been colored **{color.name}**")
            else:
                guild.waiting_on_hexcode = {}


def setup(bot):
    bot.add_cog(ColorAssignment(bot))


async def color_user(guild, user, color):
    """Color a specific user.

    Args:
        guild (Guild): The Guild object
        user (discord.Member): The member to be colors
        color (Color): The color
    """

    # remove user's current color roles
    role = guild.get_color_role(user)
    if role:
        await user.remove_roles(role)
        old_color = guild.get_color("role_id", role.id)
        if old_color:
            old_color.member_ids.discard(user.id)

    # check if role already exists and assigns then ends process if true
    if color.role_id:
        color_role = guild.get_role(color.role_id)
        if color_role:
            await user.add_roles(color_role)
        else:
            color.role_id = None  # fix role assignment

    # separated in case role is not found in above statement
    if not color.role_id:
        color_role = await guild.discord_guild.create_role(name=color.name,
                                                           color=discord.Color.from_rgb(*color.rgb))
        color.role_id = color_role.id
        await user.add_roles(color_role)

    # Report success
    color.member_ids.add(user.id)  # add user to color members
    print(f"COLORED {user} -> {color.name}")


async def add_color_UX(ctx, color, user):
    await ctx.send(f"**{color}** is not in your colors\nType the hexcode below to add it")
    guild = Guild.get(ctx.guild.id)
    guild.waiting_on_hexcode = {
        "id": ctx.author.id, "color": color, "user": user}
