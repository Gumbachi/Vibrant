import random
from random import randint
from itertools import islice, cycle, repeat

import discord
from discord.ext import commands
from rapidfuzz import process

import database as db
from classes import Guild, Color
from authorization import authorize, MissingPermissions, NotFoundError
from converters import ColorConverter
from vars import bot, emoji_dict
from utils import check_hex


class ColorAssignment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="color", aliases=["colour", "cu"])
    async def color(self, ctx, member: discord.Member, *, color: ColorConverter = None):
        """Color a specified user a specified color.

        Args:
            member (discord.Member): The member to be colored
            color (Color): The desired color
        """
        authorize(ctx, "disabled", "roles", "colors")
        guild = Guild.get(ctx.guild.id)

        # Waiting on hexcode
        if color == "waiting":
            return

        # Random color if not given
        if not color:
            color = random.choice(guild.colors)

        await color_user(guild, member, color)

        # Respond in channel
        color_embed = discord.Embed(
            title=f"Colored {member.name} **{color.name}**",
            color=color.to_discord())
        await ctx.send(embed=color_embed)

        db.update_prefs(guild)  # Update Database

    @commands.command(name="colorme", aliases=["me", "colourme"])
    async def colorme(self, ctx, *, color: ColorConverter = None):
        """Assign a Color to the author of the command."""
        authorize(ctx, "disabled", "colors")
        guild = Guild.get(ctx.guild.id)

        # Waiting on hexcode
        if color == "waiting":
            return

        # Random color selected
        if color is None:
            color = random.choice(guild.colors)

        await color_user(guild, ctx.author, color)

        # Respond in channel
        color_embed = discord.Embed(
            title=f"You are now colored **{color.name}**",
            color=color.to_discord())
        await ctx.send(embed=color_embed)

        db.update_prefs(guild)  # Update Database

    @commands.command(name="uncolorme", aliases=["uncolourme", "ucm"])
    async def uncolor_me(self, ctx):
        """Remove an existing Color from the author."""
        authorize(ctx, "disabled", has_color=ctx.author)
        guild = Guild.get(ctx.guild.id)

        # Get role and color
        role = guild.get_color_role(ctx.author)
        color = guild.get_color("role_id", role.id)

        # remove roles and update color
        await ctx.author.remove_roles(role)
        color.member_ids.discard(ctx.author.id)

        # Response
        await ctx.send(embed=discord.Embed(title="You are no longer colored"))
        db.update_prefs(guild)

    @commands.command(name="splash")
    async def color_server(self, ctx, color: ColorConverter = None):
        """Gather all of the uncolored users and assigns them a color.

        Args:
            color (str): An optional arg for coloring everyone a single color
            trace (bool): Whether or not the function should print anything
        """
        authorize(ctx, "disabled", "roles", "colors", "heavy")
        guild = Guild.get(ctx.guild.id)

        # Check for color
        if color == "waiting":
            return

        guild.heavy_command_active = ctx.command.name

        # get uncolored members
        uncolored = (member for member in ctx.guild.members
                     if not guild.get_color_role(member))

        msg = await ctx.send(embed=discord.Embed(title="Coloring everyone..."))

        # color generator for splashing
        if not color:
            color_cycle = islice(cycle(guild.colors),
                                 randint(0, len(guild.colors)-1),
                                 None)
        else:
            color_cycle = repeat(color)

        # loop and color people
        async with ctx.channel.typing():
            for member in uncolored:
                await color_user(guild, member, next(color_cycle))

        guild.heavy_command_active = None

        await msg.edit(embed=discord.Embed(title="Everyone is now colored",
                                           color=discord.Color.green()))
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

        msg = await ctx.send(embed=discord.Embed(title="Uncoloring everyone..."))
        guild.heavy_command_active = ctx.command.name

        # loop through and color members
        async with ctx.channel.typing():
            for color in guild.colors:
                # delete role
                if color.role:
                    await color.role.delete()

                color.member_ids.clear()  # Clear members from color

        guild.heavy_command_active = None
        await msg.edit(embed=discord.Embed(title="Everyone is uncolored!",
                                           color=discord.Color.green()))
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
                if guild.waiting_on_hexcode["apply"]:
                    await color_user(guild, user, color)
                    await ctx.send(f"{user.name} has been colored **{color.name}**")
                db.update_prefs(guild)
            else:
                guild.waiting_on_hexcode = {}


def setup(bot):
    bot.add_cog(ColorAssignment(bot))


async def color_user(guild, member, color):
    """Color a specific user.

    Args:
        guild (Guild): The Guild object
        user (discord.Member): The member to be colors
        color (Color): The color
    """
    dg = guild.discord_guild

    if not isinstance(member, discord.Member) or not isinstance(color, Color):
        print(type(member))
        print(type(color))
        raise Exception("COLOR USER INVALID TYPES")

    # remove user's current color role
    current_role = guild.get_color_role(member)
    if current_role:
        await member.remove_roles(current_role)

        # update old colors members
        old_color = guild.get_color("role_id", current_role.id)
        old_color.member_ids.discard(member.id)

    new_role = color.role

    # Role does not exist
    if not new_role:
        new_role = await dg.create_role(name=color.name,
                                        color=color.to_discord())
        color.role_id = new_role.id

        # get top role of bot member
        bot_roles = dg.get_member(bot.user.id).roles
        bot_role = [role for role in bot_roles if role.managed][-1]

        # put role positions under bot role
        positions = {
            new_role: bot_role.position-1,
            bot_role: bot_role.position,  # penultimate role
        }

        try:
            await dg.edit_role_positions(positions=positions)
        except:
            print("Error positioning roles")

    await member.add_roles(new_role)
    color.member_ids.add(member.id)  # add user to color members

    print(f"COLORED {member.name} -> {color.name}")
