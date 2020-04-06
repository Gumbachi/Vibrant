from random import randint
from itertools import islice, cycle, repeat

import discord
from discord.ext import commands

import database as db
from classes import Guild, Color
from authorization import authorize, MissingPermissions, NotFoundError
from vars import bot, waiting_on_reaction, waiting_on_hexcode, emoji_dict
from vars import heavy_command_active


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
                    return await add_color_UX(ctx, color_query)
                except MissingPermissions:
                    raise NotFoundError()
        else:
            color = guild.random_color()

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
                    return await add_color_UX(ctx, color_query)
                except MissingPermissions:
                    raise NotFoundError()
        else:
            color = guild.random_color()

        await color_user(guild, ctx.author, color)
        await ctx.send(f"You are now colored **{color.name}**")
        db.update_prefs(guild)

    @commands.command(name="uncolorme", aliases=["uncolourme", "ucm"])
    async def uncolor_me(self, ctx):
        """Remove an existing Color from the author"""
        authorize(ctx, "disabled", has_color=ctx.author)

        guild = Guild.get(ctx.guild.id)
        role = guild.get_color_role(ctx.author)

        # remove roles and send success message
        await ctx.author.remove_roles(role)
        await ctx.send(f"You are no longer colored **{role.name}**")
        db.update_prefs(guild)

    @commands.command(name="splash")
    async def color_server(self, ctx, color=None, trace=True):
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

        heavy_command_active[ctx.guild.id] = ctx.command.name

        # get uncolored members
        uncolored = (member for member in ctx.guild.members
                     if not guild.get_color_role(member))
        # members_to_color = sum(1 for _ in uncolored)

        # estimate time to complete
        if trace:
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
            for member, color in zip(uncolored, color_cycle):
                await color_user(guild, member, color, trace=False)

        del heavy_command_active[ctx.guild.id]

        # report success
        if trace:
            await ctx.send("Everyone visible has been colored!")

        db.update_prefs(guild)

    @commands.command(name="unsplash")
    async def uncolor_server(self, ctx, trace=True):
        """Gather all of the uncolored users and assigns them a color.

        Args:
            color (str): An optional arg for coloring everyone a single color
            trace (bool): Whether or not the function should print anything
        """
        authorize(ctx, "disabled", "roles", "heavy")

        guild = Guild.get(ctx.guild.id)

        # estimate time to complete
        if trace:
            await ctx.send("Uncoloring everyone...")

        heavy_command_active[ctx.guild.id] = ctx.command.name

        # loop through and color members
        async with ctx.channel.typing():
            for color in guild.colors:
                role = color.role
                if role:
                    await role.delete()

        del heavy_command_active[ctx.guild.id]

        # report success
        if trace:
            await ctx.send("Everyone has been uncolored!")

        db.update_prefs(guild)


def setup(bot):
    bot.add_cog(ColorAssignment(bot))


async def color_user(guild, user, color, trace=True):
    """Color a specific user.

    Args:
        guild (Guild): The username to look for
        user (discord.Member): The name or index of the color to look up
        color (Color): Whether to print anything to user
    """

    # remove user's current color roles
    role = guild.get_color_role(user)
    if role:
        await user.remove_roles(role)

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
    print(f"COLORED {user} -> {color.name}")


async def add_color_UX(ctx, color, hexcode=None):
    msg = await ctx.send(f"**{color}** is not in your colors. Would you like to add it?")
    await msg.add_reaction(emoji_dict["checkmark"])
    await msg.add_reaction(emoji_dict["crossmark"])

    waiting_on_reaction[ctx.author.id] = {
        "message": msg, "color": color}
    try:
        del waiting_on_hexcode[ctx.author.id]
    except:
        pass


# This should be a listener in the cog

# @bot.event
# async def on_reaction_add(reaction, user):
#     if user.id == bot.user.id:
#         return

#     # check reaction for adding color
#     if user.id in waiting_on_reaction.keys():
#         waiting_data = waiting_on_reaction[user.id]
#         if reaction.message.id == waiting_data["message"].id:
#             if reaction.emoji == emoji_dict["checkmark"]:
#                 await reaction.message.clear_reactions()
#                 prompt = await reaction.message.channel.send(f"{user.mention}, What will be the hexcode for **{waiting_data['color']}**")
#                 waiting_on_hexcode[user.id] = {
#                     "message": prompt, "color": waiting_data['color']}
#             elif reaction.emoji == emoji_dict["crossmark"]:
#                 await reaction.message.clear_reactions()
#                 await reaction.message.edit(content=f"{reaction.message.content} **Cancelled**")
#         else:
#             await waiting_data["message"].clear_reactions()
#             await waiting_data["message"].edit(content=f"{reaction.message.content} **Cancelled**")
#         del waiting_on_reaction[user.id]
