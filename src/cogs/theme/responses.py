from typing import TYPE_CHECKING

import discord
from common.constants import MAX_THEMES
from utils import failed_url, loading_url, success_url

if TYPE_CHECKING:
    from model import Theme

NO_THEMES_EMBED = discord.Embed(
    title="You have no themes",
    description="You can save a theme with `/theme save`\nYou can also import a preset with `preset save`"
).set_thumbnail(url=failed_url(size=48))


MAX_THEMES_EMBED = discord.Embed(
    title=f"Maximum Themes Reached ({MAX_THEMES})",
    description="Remove a theme with `/theme remove`",
    color=discord.Colour.red()
).set_thumbnail(url=failed_url(size=48))

MISSING_COLORS_FOR_THEME = discord.Embed(
    title="You have no colors",
    description="There is no point in having a theme without colors\nAdd some colors with `/color add`",
    color=discord.Color.red(),
).set_thumbnail(url=failed_url(size=48))

COULDNT_FIND_THEME = discord.Embed(
    title="Couldn't find that theme",
    description="Use the suggestions for better results."
).set_thumbnail(url=failed_url(size=48))

REMOVING_PREVIOUS_THEME = discord.Embed(
    title="Removing previous colors/theme",
    color=discord.Color.blue()
).set_thumbnail(url=loading_url())

APPLYING_THEME = discord.Embed(
    title="Applying theme...",
    color=discord.Color.blue()
).set_thumbnail(url=loading_url())


def theme_applied_embed(theme: "Theme"):
    return discord.Embed(
        title=f"{theme.name} Applied",
        color=discord.Color.green()
    ).set_thumbnail(url=success_url())


def remove_theme_sucess(theme: "Theme"):
    return discord.Embed(
        title=f"Successfully removed {theme.name}",
        color=discord.Color.green()
    )


def theme_saved_embed(theme: "Theme"):
    return discord.Embed(
        title=f"Theme saved as {theme.name}",
        color=discord.Color.green()
    )
