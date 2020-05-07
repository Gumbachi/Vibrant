import random

from discord.ext import commands
from rapidfuzz import process
from authorization import NotFoundError

from classes import Guild


class ThemeConverter(commands.Converter):
    """Convert str to theme"""
    async def convert(self, ctx, argument):
        """Converter for ease of use."""

        guild = Guild.get(ctx.guild.id)

        # get theme by index
        if argument.isdigit() and int(argument) in range(1, len(guild.themes) + 1):
            return guild.get_theme('index', int(argument))

        # get theme by name
        else:
            match = process.extractOne(
                argument, [theme.name for theme in guild.themes],
                score_cutoff=90)
            if match:
                return guild.get_theme('name', match[0])
            else:
                raise NotFoundError(argument)


class ColorConverter(commands.Converter):
    """Convert str to color"""
    async def convert(self, ctx, argument):
        """Converter for ease of use."""

        guild = Guild.get(ctx.guild.id)
        # random color
        if not argument:
            return random.choice(guild.colors)

        # get color by index
        elif argument.isdigit() and int(argument) in range(1, len(guild.colors) + 1):
            return guild.get_color('index', int(argument))

        # get color by name
        else:
            match = process.extractOne(
                query=argument,
                choices=[color.name for color in guild.colors],
                score_cutoff=90)
            if match:
                return guild.get_color('name', match[0])
            elif ctx.author.guild_permissions.manage_roles:
                await add_color_UX(ctx, argument, ctx.author)
                return "waiting"
            else:
                raise NotFoundError(argument)


async def add_color_UX(ctx, color, user):
    await ctx.send(f"**{color}** is not in your colors\nType the hexcode below to add it")
    guild = Guild.get(ctx.guild.id)
    guild.waiting_on_hexcode = {
        "id": ctx.author.id,
        "color": color,
        "user": user,
        "apply": True
    }
    if ctx.command.name == "splash":
        guild.waiting_on_hexcode["apply"] = False
