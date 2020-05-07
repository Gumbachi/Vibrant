import copy
import json
import os
from os.path import sep

import discord
from discord.ext import commands

import database as db
from authorization import authorize
from classes import Color, Guild, Theme
from converters import ThemeConverter
from vars import bot


class ThemeManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="theme.save", aliases=["t.s"])
    async def save_theme(self, ctx, *, name="None"):
        """Save a theme if there is available space"""
        authorize(ctx, "disabled", "roles", "theme_limit", "colors", name=name)
        guild = Guild.get(ctx.guild.id)

        # create Theme and add to Guild's themes
        description = "A discord color theme by " + ctx.guild.name
        if name == "None":
            name = f"Theme {len(guild.themes) + 1}"

        # copy colors and create theme
        color_copy = copy.deepcopy(guild.colors)
        theme = Theme(name, guild.id, description=description,
                      colors=color_copy)
        guild.themes.append(theme)

        await ctx.invoke(bot.get_command("themes"))
        db.update_prefs(guild)

    @commands.command(name="theme.remove", aliases=["theme.delete", "t.d", "t.r"])
    async def remove_theme(self, ctx, *, theme: ThemeConverter):
        """Remove a theme."""
        authorize(ctx, "disabled", "roles", "heavy", "themes")
        guild = Guild.get(ctx.guild.id)

        theme.delete()  # remove theme

        await ctx.invoke(bot.get_command("themes"))
        db.update_prefs(guild)

    @commands.command(name="theme.overwrite", aliases=["t.o"])
    async def overwrite_theme(self, ctx, *, theme: ThemeConverter):
        """Overwrite one of the Guild's themes with another."""
        authorize(ctx, "disabled", "heavy", "roles", "themes", "colors")
        guild = Guild.get(ctx.guild.id)

        color_copy = copy.deepcopy(guild.colors)
        new_theme = Theme(theme.name, guild.id, colors=color_copy)
        guild.themes[theme.index - 1] = new_theme

        # report success and update DB
        await ctx.send(f"**{theme.name}** has been overwritten")
        await ctx.invoke(bot.get_command("themes"))
        db.update_prefs(guild)

    @commands.command(name="theme.rename", aliases=["t.rn"])
    async def rename_theme(self, ctx, *, query):
        """Rename a theme in the guild."""
        authorize(ctx, "disabled", "roles", "themes", swap_query=query)
        guild = Guild.get(ctx.guild.id)

        # split input
        before, after = query.split("|")
        before = before.strip()
        after = after.strip()

        authorize(ctx, theme_query=(before, 80), name=after)
        theme = guild.find_theme(before, threshold=80)
        theme.name = after

        # report success
        await ctx.invoke(bot.get_command("themes"))
        db.update_prefs(guild)

    @commands.command(name="import")
    async def import_colors(self, ctx, *, name):
        """Save a preset as a theme"""
        name = name.lower()
        authorize(ctx, "disabled", "roles", "theme_limit", preset_query=name)
        guild = Guild.get(ctx.guild.id)

        # create dictionary of colors
        with open(f"presets{sep}{name}.json") as preset_data:
            preset = json.load(preset_data)

        # create theme and associate it with the guild
        theme = Theme.from_json(preset)
        theme.guild_id = ctx.guild.id
        for color in theme.colors:
            color.guild_id = ctx.guild.id
        guild.themes.append(theme)

        await ctx.send(
            f"Theme added! Apply it with `{ctx.prefix}theme.load {theme.name}`")
        await ctx.invoke(bot.get_command("themes"))
        db.update_prefs(guild)


def setup(bot):
    bot.add_cog(ThemeManagement(bot))
