import io
import json
import os
from random import randint
import re

import asyncio
import discord
from discord.ext import commands, tasks
from fuzzywuzzy import process

import functions
from functions import is_disabled, update_prefs, check_hex
from functions import pfp_analysis, draw_presets, hex_to_rgb
import vars
from vars import bot, get_prefix, waiting_on_reaction
from vars import waiting_on_pfp, waiting_on_hexcode
from classes import Color, Guild
from cfg import coll


class Colors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="colors", aliases=["colours", "c"])
    async def show_colors(self, ctx):
        """Display an image of equipped colors."""
        guild = Guild.get(ctx.guild.id)
        fp = io.BytesIO(guild.draw_colors())  # convert to sendable

        # send info to channel or user
        if not await authorize(ctx, checks=["disabled"], trace=False):
            await ctx.author.send(content=f"**{ctx.guild.name}**:",
                                  file=discord.File(fp, filename="colors.png"))
        else:
            await ctx.send(file=discord.File(fp, filename="colors.png"))

    @commands.command(name="color", aliases=["colour", "cu"])
    async def color(self, ctx, user, *color):
        """
        Color a specified user a specified color.

        Args:
            user (str): The name of the user or a mention
            color (tuple of str): The name of the desired color
        """
        if not await authorize(ctx):
            return

        await color_user(ctx, user, " ".join(color), trace=True)
        await update_prefs([Guild.get(ctx.guild.id)])

    @commands.command(name="colorme", aliases=["me", "colourme", "cm"])
    async def colorme(self, ctx, *color):
        """
        Assign a Color to the author of the command.

        Args:
            color (tuple of str): The name of the color
        """
        if not await authorize(ctx, checks=["disabled"]):
            return

        await color_user(ctx, ctx.author.name, " ".join(color))
        await update_prefs([Guild.get(ctx.guild.id)])

    @commands.command(name="uncolorme", aliases=["uncolourme", "ucm"])
    async def uncolor_me(self, ctx):
        """Remove an existing Color from the author"""
        if not await authorize(ctx, checks=["disabled"]):
            return

        # get role to remove
        guild = Guild.get(ctx.guild.id)
        role = guild.get_color_role(ctx.author)
        if not role:
            return await ctx.send("You don't have a color to remove")

        # remove roles and send success message
        await ctx.author.remove_roles(role)
        await ctx.send(f"You are no longer colored **{role.name}**")

    @commands.command(name="splash", aliases=["colorall", "colourall"])
    async def color_server(self, ctx, color=None, trace=True):
        """
        Gather all of the uncolored users and assigns them a color.

        Args:
            color (str): An optional arg for coloring everyone a single color
            trace (bool): Whether or not the function should print anything
        """
        if not await authorize(ctx):
            return

        guild = Guild.get(ctx.guild.id)

        # check if there are colors
        if not guild.colors and trace:
            return await ctx.send(embed=vars.none_embed)

        # get specific color
        if color:
            color = guild.find_color(color)
            if not color:
                return await ctx.send("Couldn't find that color")

        # get uncolored members
        uncolored = [member.name for member in ctx.guild.members
                     if not guild.get_color_role(member)]

        # estimate time to complete
        if trace:
            await ctx.send(
                ("Coloring everyone will take around "
                 f"{len(uncolored)/2 + (10 * (len(uncolored)//10))} seconds"))

        # loop through and color members
        async with ctx.channel.typing():
            amt_colors = len(guild.colors)
            index = randint(1, amt_colors) if not color else color.index
            for name in uncolored:
                # keep index in range
                if index > len(guild.colors):
                    index = 1

                await color_user(ctx, name, str(index), trace=False)

                # increment index
                if not color:
                    index += 1

        # report success
        if trace:
            await ctx.send("Success! Everyone visible has been colored")
        await update_prefs([guild])

    @commands.command(name="clear_all_colors", aliases=["clear_all_colours"])
    async def clear_colors(self, ctx, backup=True):
        """
        Remove all colors from the Guild's colors.

        Args:
            backup (bool): Whether or not to send a backup JSON
        """
        if not await authorize(ctx):
            return

        guild = Guild.get(ctx.guild.id)

        # provide backup JSON
        if backup:
            await ctx.invoke(bot.get_command("export"), trace=False)

        # remove all colors and clear roles
        async with ctx.channel.typing():
            await guild.clear_colors()
        await ctx.send(f"Success! All colors have been removed.")

        await update_prefs([guild])

    @commands.command(name="add", aliases=["new", "create", "addcolor", "a"])
    async def add_color(self, ctx, hexcode, *name):
        """
        Add a color to the Guild's active colors.

        Args:
            hexcode (str): The hexcode of the new color
            name (tuple of str): The name of the new color
        """
        if not await authorize(ctx):
            return

        # check name length
        name = " ".join(name)
        if len(name) > 99:
            raise commands.UserInputError(f"**{name}** is too long")

        guild = Guild.get(ctx.guild.id)

        # check color limit
        if len(guild.colors) >= guild.color_limit:
            return await ctx.send("You've reached the max amount of colors")

        # use regex to verify proper input
        if re.search(r"[\S]+", name) is None:
            name = f"Color {len(guild.colors) + 1}"
        if re.search(r"[|]+", name):
            raise commands.UserInputError(
                "You cannot use the `|` symbol in color names")

        # verify hexcode
        if check_hex(hexcode):
            # change black color because #000000 in discord is transparent
            if hexcode == "#000000":
                hexcode == "#000001"
            color = Color(name, hexcode, ctx.guild.id)
            guild.colors.append(color)
        else:
            raise commands.UserInputError(
                f"**{hexcode}** is invalid. Proper format is: #123abc")

        # report success
        await ctx.send(
            f"**{color.name}** has been added at index **{color.index}**.")
        await ctx.invoke(bot.get_command("colors")) # show new set
        await update_prefs([guild])

    @commands.command(name="remove", aliases=["delete", "r"])
    async def remove_color(self, ctx, *query):
        """
        Remove a color from the Guild's colors

        Args:
            color (tuple of str): The search query for color to remove
        """
        if not await authorize(ctx):
            return

        # get name and colors
        guild = Guild.get(ctx.guild.id)
        colors = guild.colors
        query = " ".join(query)

        # verify input and prep
        if not colors:
            return await ctx.send(embed=vars.none_embed)

        # find color
        color = guild.find_color(query, 95)
        if not color:
            raise commands.UserInputError(
                f"Couldn't find **{query}**. Try using an index or type `{get_prefix(bot, ctx.message)}help remove` for more help")

        # remove color and response
        await color.delete()
        await ctx.send(f"**{color.name}** has been deleted!")

        await ctx.invoke(bot.get_command("colors"))  # show updated set

    @commands.command(name="rename", aliases=["rn"])
    async def rename_color(self, ctx, *query):
        """
        Rename a color in the Guild's active colors.

        Args:
            color (tuple of str): The color to change the name of
        """
        if not await authorize(ctx):
            return

        query = " ".join(query)
        guild = Guild.get(ctx.guild.id)

        # check if there are colors
        if not guild.colors:
            return await ctx.send(embed=vars.none_embed)

        # verify input
        if not re.search(r"[\d\w\s]+[|]{1}[\d\w\s]+", query):
            raise commands.UserInputError(f"**{query}** is not a valid input")

        try:
            before, after = query.split("|")
        except:
            raise commands.UserInputError(
                f"There are too many separators in **{query}**")

        # strip extraneous spaces
        before = before.strip()
        after = after.strip()

        # change color and update preferences
        response = await change_color(guild, before, after, "name")
        await ctx.send(response)
        await update_prefs([guild])

    @commands.command(name="recolor", aliases=["recolour", "rc"])
    async def recolor(self, ctx, *query):
        """
        Change a color's hexcode in the Guild's active colors.

        Args:
            color (tuple of str): The color to change the hexcode of
        """
        if not await authorize(ctx):
            return

        query = " ".join(query)
        guild = Guild.get(ctx.guild.id)

        # check if there are colors
        if not guild.colors:
            return await ctx.send(embed=vars.none_embed)

        # verify input
        if not re.search(r"[\d\w\s]+[|]{1}[\d\w\s]+", query):
            raise commands.UserInputError(f"**{query}** is not a valid input")
        try:
            before, after = query.split("|")
        except:
            raise commands.UserInputError(
                f"There are too many separators in **{query}**")

        # strip extraneous spaces
        before = before.strip()
        after = after.strip()

        # change color and update preferences
        response = await change_color(guild, before, after, "color")
        await ctx.send(response)
        await update_prefs([guild])

    @commands.command(name="info", aliases=["about"])
    async def show_color_info(self, ctx, color_name):
        guild = Guild.get(ctx.guild.id)

        color = guild.find_color(color_name, threshold=0)
        print(color)
        if not color:
            raise commands.UserInputError(
                f"Couldn't find {color_name}. Try using an index for more accurate results")

        member_names = [bot.get_user(id).name for id in color.members]
        color_embed = discord.Embed(
            title=color.name,
            description=(f"Hexcode: {color.hexcode}\n"
                         f"RGB: {color.rgb()}\n"
                         f"Members: {', '.join(member_names)}\n"
                         f"Index: {color.index}\n"
                         f"Role ID: {color.role_id}"),
            color=discord.Color.from_rgb(*color.rgb()))

        # manage recipient and cleanup if needed
        if not await authorize(ctx, checks=["disabled"], trace=False):
            await ctx.author.send(embed=color_embed)  # to user
        else:
            await ctx.send(embed=color_embed)

    @commands.command("pfp")
    async def get_pfp_color(self, ctx, *name):
        """Use an algorithm to find the most prominent color in a pfp."""
        guild = Guild.get(ctx.guild.id)
        user = " ".join(name)

        # get the best user
        if user == "":
            user = ctx.author
        else:
            user = guild.find_user(user, ctx.message, 0)

        hexcode = pfp_analysis(user.avatar_url)

        if not await authorize(ctx, checks=["disabled"], trace=False):
            await ctx.author.send(f"**{hexcode}** matches {user.name}'s profile picture.")
        else:
            await ctx.send(f"**{hexcode}** matches {user.name}'s profile picture.")

        # prompt to add to colors
        if ctx.author.guild_permissions.manage_roles:
            prompt = await ctx.send(f"Would you like to add {hexcode} to your colors?")
            return await add_color_UX(prompt, ctx.author, user.name, hexcode=hexcode)




    # export colors data in json format
    @commands.command("export")
    async def export_colors(self, ctx, trace=True):
        # check for colors
        if not Guild.get(ctx.guild.id).colors:
            return await ctx.send(embed=vars.none_embed)

        # find guild in database and convert to bytes
        if coll.find_one({"id": ctx.guild.id}) is not None:
            colors = coll.find_one({"id": ctx.guild.id})["colors"]
            data = json.dumps(colors, indent=2).encode("utf-8")
            bytes_data = io.BytesIO(data)

            # send data in JSON format
            if trace:
                return await ctx.send(f"JSON file for **{ctx.guild.name}**'s colors:", file=discord.File(bytes_data, filename=f"{ctx.guild.name}_colors.json"))
            else:
                return await ctx.send(file=discord.File(bytes_data, filename=f"{ctx.guild.name}_backup.json"))
        else:
            return Exception("Couldn't find guild. Must be a database error")


def setup(bot):
    bot.add_cog(Colors(bot))


async def color_user(ctx, quser, qcolor, trace=True):
    """
    Color a specific user.

    Args:
        quser (str): The username to look for
        qcolor (str): The name or index of the color to look up
        trace (bool): Whether to print anything to user
    """
    guild = Guild.get(ctx.guild.id)

    # check for empty colors
    if not guild.colors and trace:
        return await ctx.send(embed=vars.none_embed)

    # find user
    user = guild.find_user(quser, ctx.message)
    if not user:
        raise commands.UserInputError(
            f"Couldn't find **{quser}**. You should mention a user for a 100% success rate")

    # find color
    color = guild.find_color(qcolor)
    if not color:
        if ctx.author.guild_permissions.manage_roles:
            prompt = await ctx.send(f"Couldn't find that color. Would you like to add **{qcolor}**?")
            return await add_color_UX(prompt, ctx.author, qcolor)
        else:
            raise commands.UserInputError(
                f"Couldn't find **{qcolor}**. Try again with an index or more precise name")

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
    if not color.role_id:
        color_role = await ctx.guild.create_role(name=color.name, color=discord.Color.from_rgb(*color.rgb()))
        color.role_id = color_role.id
        await user.add_roles(color_role)

    # Report success
    print(f"COLORED {user} -> {color.name}")
    if trace:
        await ctx.send(f"Gave **{user.name}** the **{color_role.name}** role")

async def change_color(guild, q1, q2, action):
    """
    Swap the color or name of a Color object.

    Args:
        guild (Guild): The Guild to adjust
        q1 (str): The search query for the color to change
        q2 (str): The new name or hexcode
        action (str): which action to perform
    """
    # find color to change
    color = guild.find_color(q1, threshold=90)
    if not color:
        raise commands.UserInputError(
            f"Couldn't find **{q1}**. Try using a color's index for better results")

    response = None
    # rename the color
    if action == "name":
        response = f"Renamed **{color.name}** to **{q2}**"
        color.name = q2

    # change the hexcode of the color
    if action == "color":
        if check_hex(q2):
            response = f"**{color.name}** is now colored **{q2}**"
            color.hexcode = q2
        else:
            raise commands.UserInputError(
                f"**{q2}** is an invalid hex code.Proper Format: #123abc")

    # adjust roles if color is changed
    if color.role_id:
        role = guild.get_role(color.role_id)
        await role.edit(name=color.name,
                        color=discord.Color.from_rgb(*color.rgb()))
    return response

async def add_color_UX(message, author, color, hexcode=None):
    await message.add_reaction(vars.emoji_dict["checkmark"])
    await message.add_reaction(vars.emoji_dict["crossmark"])
    if not hexcode:
        waiting_on_reaction[author.id] = {"message": message, "color": color}
        try:
            del vars.waiting_on_hexcode[author.id]
        except:
            pass
    else:
        waiting_on_pfp[author.id] = {
            "message": message, "color": color, "hexcode": hexcode}

async def authorize(ctx, checks=["disabled", "manage_roles"], trace=True):
    """Check channel status and verify manage role perms"""
    # check channel status
    if "disabled" in checks:
        if is_disabled(ctx.channel):
            await ctx.message.delete()
            if trace:
                await ctx.author.send(f"#{ctx.channel.name} is disabled")
            return False

    # verify author's permissions
    if "manage_roles" in checks:
        if not ctx.author.guild_permissions.manage_roles:
            if trace:
                await ctx.send("You need `manage roles` permission to use this command")
            return False
    return True

@bot.event
async def on_reaction_add(reaction, user):
    if user.id == bot.user.id:
        return

    # check reaction for adding color
    if user.id in waiting_on_reaction.keys():
        waiting_data = waiting_on_reaction[user.id]
        if reaction.message.id == waiting_data["message"].id:
            if reaction.emoji == vars.emoji_dict["checkmark"]:
                await reaction.message.clear_reactions()
                prompt = await reaction.message.channel.send(f"{user.mention}, What will be the hexcode for **{waiting_data['color']}**")
                waiting_on_hexcode[user.id] = {
                    "message": prompt, "color": waiting_data['color']}
            elif reaction.emoji == vars.emoji_dict["crossmark"]:
                await reaction.message.clear_reactions()
                await reaction.message.edit(content=f"{reaction.message.content} **Cancelled**")
        else:
            await waiting_data["message"].clear_reactions()
            await waiting_data["message"].edit(content=f"{reaction.message.content} **Cancelled**")
        del waiting_on_reaction[user.id]

    # check reaction for adding pfp color
    if user.id in waiting_on_pfp.keys():
        pfp_data = waiting_on_pfp[user.id]
        ctx = await bot.get_context(pfp_data["message"])
        if reaction.message.id == pfp_data["message"].id:
            if reaction.emoji == vars.emoji_dict["checkmark"]:
                await reaction.message.clear_reactions()
                await ctx.invoke(bot.get_command("add"), pfp_data["hexcode"], pfp_data["color"])
            elif reaction.emoji == vars.emoji_dict["crossmark"]:
                await reaction.message.delete()
        else:
            await pfp_data["message"].delete()
        del waiting_on_pfp[user.id]
