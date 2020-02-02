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
        guild = Guild.get(ctx.guild.id)
        fp = io.BytesIO(guild.draw_themes())  # convert to sendable

        #send to author or channel depending on status
        if is_disabled(ctx.channel):
            await ctx.message.delete()
            await ctx.author.send(f"**{ctx.guild.name}**:",
                                  file=discord.File(fp, filename="themes.png"))
        else:
            await ctx.send(file=discord.File(fp, filename="themes.png"))

    @commands.command(name="theme.save")
    async def save_theme(self, ctx, *name):
        """Save a theme if there is available space"""
        if not await authorize(ctx):
            return

        guild = Guild.get(ctx.guild.id)

        # check if guild is at limit
        if len(guild.themes) >= guild.theme_limit:
            return await ctx.send(("You've reached the max amount of themes."
                                   "You can remove unwanted themes by using"
                                   "the `removetheme` command"))

        # check color availability
        if not guild.colors:
            return await ctx.send("There are no colors to save!")

        # create Theme and add to Guild's themes
        description = "A discord color theme by " + ctx.guild.name
        name = " ".join(name)
        if name == "":
            name = f"Theme {len(guild.themes) + 1}"
        color_copy = copy.deepcopy(guild.colors)
        theme = Theme(name, guild.id, description, color_copy)
        guild.themes.append(theme)

        # report success
        await ctx.send(f"Theme has been saved as **{name}**")
        await ctx.invoke(bot.get_command("themes"))
        await update_prefs([guild])

    @commands.command(name="theme.overwrite")
    async def overwrite_theme(self, ctx, *query):
        """Overwrite one of the Guild's themes with another."""
        if not await authorize(ctx):
            return

        guild = Guild.get(ctx.guild.id)

        if not guild.colors:
            return await ctx.send("There are no colors to save!")

        # verify input
        query = " ".join(query)
        if not re.search(r"[\d\w\s]+[|]{1}[\d\w\s]+", query):
            raise commands.UserInputError("Invalid input")
        try:
            before, after = query.split("|")
        except:
            raise commands.UserInputError(
                "There are too many separators in your input")

        # cut extraneous spaces
        before = before.strip()
        after = after.strip()

        # find theme and check if found
        theme_to_replace = guild.find_theme(before, threshold=100)
        if not theme_to_replace:
            raise commands.UserInputError(
                f"Couldn't find a theme named **{before}**")

        index = theme_to_replace.index - 1
        old_name = theme_to_replace.name
        theme_to_replace.delete()
        description = f"A discord color theme by {ctx.guild.name}"

        # create deep copy so that theme and guild dont point to same list
        color_copy = copy.deepcopy(guild.colors)
        new_theme = Theme(after, guild.id, description, color_copy)
        guild.themes.insert(index, new_theme)

        # report success and update DB
        await ctx.send(
            f"**{old_name}** has been replaced by **{new_theme.name}**")
        await ctx.invoke(bot.get_command("themes"))
        await update_prefs([guild])

    @commands.command(name="theme.load", aliases=["st"])
    async def load_theme(self, ctx, *query):
        """Change the active colors to a theme."""
        if not await authorize(ctx):
            return

        guild = Guild.get(ctx.guild.id)

        if not guild.themes:
            return await ctx.send("There are no themes to switch to")

        # try to find theme
        theme = guild.find_theme(" ".join(query), threshold=90)
        if not theme:
            raise commands.UserInputError("Couldn't find that theme!")

        print("Loading theme")

        # clear colors
        await guild.clear_colors()

        # apply colors
        theme.activate()
        async with ctx.channel.typing():
            for color in guild.colors:
                if color.members:
                    for id in color.members:
                        user = bot.get_user(id)
                        if user:
                            await color_user(ctx, user.name, color.name, False)

        # report success and update DB
        await ctx.send(
            f"Loaded **{theme.name}**")
        await ctx.invoke(bot.get_command("themes"))
        await update_prefs([guild])

    @commands.command(name="theme.remove", aliases=["deletetheme", "dt"])
    async def remove_theme(self, ctx, *query):
        """Remove a theme."""
        if not await authorize(ctx):
            return

        guild = Guild.get(ctx.guild.id)

        if not guild.themes:
            return await ctx.send("There are no themes to remove")

        # try to find theme
        theme = guild.find_theme(" ".join(query), threshold=90)
        if not theme:
            return await ctx.send("Couldn't find that theme!")

        theme.delete()

        # report success
        await ctx.send(f"Deleted **{theme.name}**")
        await ctx.invoke(bot.get_command("themes"))
        await update_prefs([guild])

    @commands.command(name="theme.rename", aliases=["trename"])
    async def rename_theme(self, ctx, *query):
        """Rename a theme in the guild."""
        if not await authorize(ctx):
            return

        guild = Guild.get(ctx.guild.id)

        if not guild.themes:
            return await ctx.send("There are no themes to rename")

        # verify input
        query = " ".join(query)
        if not re.search(r"[\d\w\s]+[|]{1}[\d\w\s]+", query):
            raise commands.UserInputError("Invalid input")
        try:
            before, after = query.split("|")
        except:
            raise commands.UserInputError(
                "There are too many separators in your input")

        # strip extraneous spaces
        before = before.strip()
        after = after.strip()

        # try to find theme
        theme = guild.find_theme(before, threshold=80)
        if not theme:
            raise commands.UserInputError("couldn't find that theme")

        # report success
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

        guild = Guild.get(ctx.guild.id)

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

    @commands.command(name="theme.info")
    async def theme_info(self, ctx, query):
        """Get general info about a theme."""
        guild = Guild.get(ctx.guild.id)
        query = " ".join(query)

        # try to find theme
        theme = guild.find_theme(query, threshold=0)
        if not theme:
            raise commands.UserInputError(
                f"Couldn't find {query}. Try using an index for more accurate results")

        # generate embed
        theme_embed = discord.Embed(
            title=theme.name,
            description=(f"Description: {theme.description}\n"
                         f"Index: {theme.index}\n"
                         f"Colors: {', '.join([color.name for color in theme.colors])}"),
            color=discord.Color.blurple())

        # manage recipient and cleanup if needed
        if not await authorize(ctx, checks=["disabled"], trace=False):
            await ctx.author.send(embed=theme_embed)
        else:
            await ctx.send(embed=theme_embed)


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
