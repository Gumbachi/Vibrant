import copy
import io
import re
import json
from os.path import sep

import discord
from discord.ext import commands

from cogs.colors import color_user

from classes import Color, Guild, Theme
from functions import is_disabled, update_prefs
from vars import bot, preset_names


class Themes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="themes")
    async def show_themes(self, ctx):
        """Draw the guild's themes and send in channel"""
        guild = Guild.get_guild(ctx.guild.id)
        fp = io.BytesIO(guild.draw_themes())  # convert to sendable

        #send to author or channel depending on status
        if is_disabled(ctx.channel):
            await ctx.message.delete()
            await ctx.author.send(f"**{ctx.guild.name}**:",
                                  file=discord.File(fp, filename="themes.png"))
        else:
            await ctx.send(file=discord.File(fp, filename="themes.png"))

    @commands.command(name="save")
    async def save_theme(self, ctx, *name):
        if is_disabled(ctx.channel):
            await ctx.message.delete()  # delete command if disabled
            return await ctx.author.send(f"#{ctx.channel.name} is disabled")

        if not ctx.author.guild_permissions.manage_roles:
            return await ctx.send(
                "You need the `manage roles` permission to use this command")

        guild = Guild.get_guild(ctx.guild.id)

        if len(guild.themes) >= guild.theme_limit:
            return await ctx.send(("You've reached the max amount of themes."
                                   "You can remove unwanted themes by using"
                                   "the `removetheme` command"))

        if not guild.colors:
            return await ctx.send("There are no colors to save!")

        description = "A discord color theme by " + ctx.guild.name
        name = " ".join(name)
        if name == "":
            name = f"Theme {len(guild.themes) + 1}"
        theme = Theme(name, guild.id, description)
        color_copy = copy.deepcopy(guild.colors)
        theme.colors = color_copy
        guild.themes.append(theme)
        await ctx.send(f"Theme has been saved as **{name}**")
        await ctx.invoke(bot.get_command("themes"))
        await update_prefs([guild])


    @commands.command(name="theme", aliases=["st"])
    async def change_theme(self, ctx, query):
        if is_disabled(ctx.channel):
            await ctx.message.delete()  # delete command if disabled
            return await ctx.author.send(f"#{ctx.channel.name} is disabled")

        if not ctx.author.guild_permissions.manage_roles:
            return await ctx.send("You need the `manage roles` permission to use this command")

        guild = Guild.get_guild(ctx.guild.id)

        if not guild.themes:
            return await ctx.send("There are no themes to switch to")

        theme = guild.find_theme(query, threshold=90)

        if not theme:
            return await ctx.send("Couldn't find that theme!")

        await guild.clear_colors()
        theme.activate()
        async with ctx.channel.typing():
            for color in guild.colors:
                print(color)
                if color.members:
                    for id in color.members:
                        user = bot.get_user(id)
                        if user:
                            await color_user(ctx, user.name, (color.name,), False)
        await ctx.invoke(bot.get_command("themes"))
        await update_prefs([guild])

    # remove themes
    @commands.command(name="removetheme", aliases=["deletetheme", "deltheme", "dt"])
    async def remove_theme(self, ctx, query):
        if is_disabled(ctx.channel):
            await ctx.message.delete()  # delete command if disabled
            return await ctx.author.send(f"#{ctx.channel.name} is disabled")

        if not ctx.author.guild_permissions.manage_roles:
            return await ctx.send("You need the `manage roles` permission to use this command")

        guild = Guild.get_guild(ctx.guild.id)

        if not guild.themes:
            return await ctx.send("There are no themes to remove")

        theme = guild.find_theme(query, threshold=90)

        if not theme:
            return await ctx.send("Couldn't find that theme!")

        theme.delete()

        await ctx.send("Theme Deleted")
        await update_prefs([guild])
        await ctx.invoke(bot.get_command("themes"))

    # rename themes
    @commands.command(name="renametheme", aliases=["trename"])
    async def rename_theme(self, ctx, *query):
        if is_disabled(ctx.channel):
            await ctx.message.delete()  # delete command if disabled
            return await ctx.author.send(f"#{ctx.channel.name} is disabled")

        if not ctx.author.guild_permissions.manage_roles:
            return await ctx.send("You need the `manage roles` permission to use this command")

        guild = Guild.get_guild(ctx.guild.id)

        if not guild.themes:
            return await ctx.send("There are no themes to rename")

        query = " ".join(query)
        if not re.search(r"[\d\w\s]+[|]{1}[\d\w\s]+", query):
            return await ctx.send("Invalid input")
        try:
            before, after = query.split("|")
        except:
            return await ctx.send("There are too many separators in your input")

        before = before.strip()
        after = after.strip()

        theme = guild.find_theme(before, threshold=80)
        if not theme:
            return await ctx.send("couldn't find that theme")

        await ctx.send(f"**{theme.name}** has been renamed to **{after}**")
        theme.name = after
        await update_prefs([guild])


    @commands.command("import")
    async def import_colors(self, ctx, name):
        """Save a preset as a theme"""
        if not await authorize(ctx):
            return

        # check if preset exists
        if name not in preset_names:
            raise commands.UserInputError(
                f"**{name}** is not the name of a preset")

        guild = Guild.get_guild(ctx.guild.id)

        # make sure guild is not at theme limit
        if len(guild.themes) >= guild.theme_limit:
            return await ctx.send(
                "You have too many themes delete one and try again")

        # create dictionary of colors
        with open(f"presets{sep}{name}.json") as preset_data:
            preset = json.load(preset_data)

        # create theme and associate it with the guild
        theme = Theme.from_json(preset)
        theme.guild_id = ctx.guild.id
        for color in theme.colors:
            color.guild_id = ctx.guild.id
        guild.themes.append(theme)
        guild.reindex_themes()

        await ctx.send(
            f"Preset has been saved as **{theme.name}** in your themes")
        await update_prefs([guild])  # update MongoDB

    # info


def setup(bot):
    bot.add_cog(Themes(bot))

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
