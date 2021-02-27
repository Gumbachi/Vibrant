import json
from os.path import sep

from discord.ext import commands
from discord.ext.commands import CommandError, UserInputError

import common.database as db
import common.cfg as cfg
from common.utils import ThemeConverter, heavy_command_not_running, theme_lookup


class ThemeManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        """Ensure user has permissions and heavy command is not active for cog commands."""
        if not ctx.author.guild_permissions.manage_roles:
            raise CommandError(f"You need Manage Roles permission")
        return True

    @commands.command(name="save", aliases=["t.s", "theme.save", "saveas"])
    async def save_theme(self, ctx, *, name=""):
        """Save the current state of the guilds colors"""
        colors, themes = db.get_many(ctx.guild.id, "colors", "themes")

        if not colors:
            raise CommandError("There must be colors to save a theme")

        if len(themes) >= cfg.theme_limit:
            raise CommandError(f"Theme Limit Reached ({len(themes)}/10)")

        # Verufy name
        if "|" in name or len(name) >= 100:
            raise UserInputError(
                "Color names must be shorter than 100 characters and cannot include `|`")

        if not name:
            name = f"Theme {len(themes) + 1}"

        # Remove unnecessary role attribute from database
        for color in colors:
            del color["role"]

        # create and add color
        new_theme = {
            "name": name,
            "colors": colors,
        }

        # update database
        db.guilds.update_one(
            {"_id": ctx.guild.id},
            {"$push": {"themes": new_theme}}
        )
        await ctx.invoke(self.bot.get_command("themeinfo"))  # show new set

    @commands.command(name="theme.remove", aliases=["theme.delete", "erase"])
    async def remove_theme(self, ctx, *, theme: ThemeConverter):
        """Remove a theme."""
        db.guilds.update_one(
            {"_id": ctx.guild.id},
            {"$pull": {"themes": theme}}
        )
        await ctx.invoke(self.bot.get_command("themeinfo"))

    @commands.command(name="theme.overwrite", aliases=["overwrite"])
    @commands.check(heavy_command_not_running)
    async def overwrite_theme(self, ctx, *, themename):
        """Overwrite one of the Guild's themes with another."""

        colors, themes = db.get_many(ctx.guild.id, "colors", "themes")

        old_theme = theme_lookup(themename, themes)
        if not old_theme:
            raise UserInputError("Could not find that theme")

        # Remove unnecessary role attribute from database
        for color in colors:
            del color["role"]

        # create and add color
        new_theme = {
            "name": old_theme["name"],
            "colors": colors,
        }

        # update database
        db.guilds.update_one(
            {"_id": ctx.guild.id, "themes": old_theme},
            {"$set": {"themes.$": new_theme}}
        )
        await ctx.invoke(self.bot.get_command("themeinfo"))

    @commands.command(name="theme.rename", aliases=["t.rn"])
    async def rename_theme(self, ctx, *, query):
        """Rename a theme in the guild."""
        themes = db.get(ctx.guild.id, "themes")

        try:
            before, after = query.split("|")
        except ValueError:
            raise UserInputError(
                "Command should be formatted as: $t.rn <theme> | <name>")

        # Find the correct color to remove. or dont.
        theme = theme_lookup(before.strip(), themes)
        if not theme:
            raise UserInputError("Couldn't find that theme")

        after = after.strip()
        if not after:
            raise UserInputError(
                "Command should be formatted as: $rename <color> | <name>")

        db.guilds.update_one(
            {"_id": ctx.guild.id, "themes": theme},
            {"$set": {"themes.$.name": after}}
        )
        await ctx.invoke(self.bot.get_command("themeinfo"))

    @commands.command(name="import")
    async def import_colors(self, ctx, *, name):
        """Save a preset as a theme."""
        themes = db.get(ctx.guild.id, "themes")

        if len(themes) >= cfg.theme_limit:
            raise CommandError(f"Theme Limit Reached ({len(themes)}/10)")

        # Read in preset as dict
        name = name.replace(" ", "")
        try:
            with open(f"assets{sep}presets{sep}{name.lower()}.json") as preset_data:
                preset = json.load(preset_data)
        except FileNotFoundError:
            raise UserInputError("Could not find that preset")

        db.guilds.update_one(
            {"_id": ctx.guild.id},
            {"$push": {"themes": preset}}
        )
        await ctx.invoke(self.bot.get_command("tinfo"))


def setup(bot):
    bot.add_cog(ThemeManagement(bot))
