from typing import TYPE_CHECKING

import discord
from common.constants import MAX_COLORS
from utils.emoji import failed_url, loading_url, success_url

if TYPE_CHECKING:
    from model import Color

NO_COLORS_EMBED = discord.Embed(
    title=f"You have no colors",
    description="Use `/color add` to add some"
).set_thumbnail(url=failed_url(size=48))


MAX_COLORS_EMBED = discord.Embed(
    title=f"Maximum Colors Reached",
    description=f"You can have up to {MAX_COLORS} colors",
    color=discord.Colour.red()
).set_thumbnail(url=failed_url(size=48))


COULDNT_FIND_COLOR = discord.Embed(
    title=f"Couldn't find that color",
    description=f"Be sure to use the autocomplete suggestions",
    color=discord.Colour.red()
).set_thumbnail(url=failed_url(size=48))


def color_applied_embed(color: "Color", person: discord.Member):
    return discord.Embed(
        title=f"Colored {person.display_name} {color.name}",
        color=color.to_discord_color()
    ).set_thumbnail(url=success_url())


INVALID_COLOR_VALUE = discord.Embed(
    title=f"Invalid color value",
    description="[Color Picker](https://htmlcolorcodes.com)"
).set_thumbnail(url=failed_url(size=48))

INVALID_COLOR_NAME = discord.Embed(
    title="Name must be 1-99 characters",
    color=discord.Color.red()
).set_thumbnail(url=failed_url())


def add_color_success(color: "Color"):
    return discord.Embed(
        title=f"Added {color.name}",
        color=color.to_discord_color()
    ).set_thumbnail(url=success_url())


def remove_color_success(color: "Color"):
    return discord.Embed(
        title=f"Removed {color.name}",
        color=color.to_discord_color()
    ).set_thumbnail(url=success_url())


GETTING_THINGS_READY = discord.Embed(
    title="Getting Things Ready..",
    color=discord.Color.blue()
).set_thumbnail(url=loading_url())

SPLASH_COLORING_PEOPLE = discord.Embed(
    title="Coloring People...",
    description="This may take a while",
    color=discord.Color.blue()
).set_thumbnail(url=loading_url(size=48))

UNSPLASH_SUCCESS = discord.Embed(
    title="Uncolored Everybody",
    color=discord.Color.green()
).set_thumbnail(url=success_url())


def splash_successful(amount: int):
    return discord.Embed(
        title=f"Colored {amount} people",
        color=discord.Color.green()
    ).set_thumbnail(url=success_url())


REMOVING_COLORS = discord.Embed(
    title="Removing Colors...",
    color=discord.Color.blue()
).set_thumbnail(url=loading_url())

CLEAR_COLORS_SUCCESS = discord.Embed(
    title=f"Cleared All Colors"
).set_thumbnail(url=success_url())


MISSING_EDIT_INFO = discord.Embed(
    title=f"Missing New Name or Value",
    color=discord.Color.red()
).set_thumbnail(url=failed_url())

EDIT_COLOR_UNSUCCESSFUL = discord.Embed(
    title=f"Invalid Name or Value",
    color=discord.Color.red()
).set_thumbnail(url=failed_url())


def edit_successful(before: "Color", after: "Color"):
    return discord.Embed(
        title=f"Edited {before.name} into {after.name}",
        color=after.to_discord_color()
    ).set_thumbnail(url=success_url())


def error_embed(error: Exception):
    return discord.Embed(
        title="There was a problem with that",
        description="This can be caused if a heavy operation like `/splash` is running and you attempt to modify colors",
        color=discord.Color.red()
    ).set_footer(text=str(error)).set_thumbnail(url=failed_url(size=48))
