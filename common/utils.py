"""Holds helper functions."""
import re
import random

import discord
from PIL import ImageColor
from discord.ext import commands

import common.database as db
import cogs.errors as errors


def to_rgb(hexcode):
    return ImageColor.getrgb(hexcode)


class ColorConverter(commands.Converter):
    async def convert(self, ctx, arg):
        """Find a color in a list of colors based on a query"""
        colors = db.get(ctx.guild.id, "colors")

        if not colors:
            raise errors.ColorError("You have no active colors")

        color = color_lookup(arg, colors)
        if not color:
            raise errors.ColorError("Color Not Found")
        return color


def color_lookup(arg, colors):
    """Returns a color or None"""
    # random color
    if arg == "":
        return random.choice(colors)

    # Index lookup
    elif arg.isdigit():
        try:
            return colors[int(arg)-1]
        except IndexError:
            pass

    # Name lookup
    else:
        for color in colors:
            if color["name"].lower() == arg.lower():
                return color


def validate_hex(hexcode):
    """Validate a hex code."""
    return bool(re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', hexcode))


def validate_color_name(name):
    return bool()


def discord_color(color):
    """converts a color to a discord color for embeds"""
    return discord.Color.from_rgb(*to_rgb(color["hexcode"]))
