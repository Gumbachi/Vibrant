from typing import TYPE_CHECKING

import discord
from utils import failed_url, success_url

if TYPE_CHECKING:
    from model import Theme

COULDNT_FIND_PRESET = discord.Embed(
    title="Couldn't find that preset",
    description=f"Be sure to use the autocomplete suggestions",
    color=discord.Colour.red()
).set_thumbnail(url=failed_url(size=48))


def preset_saved_embed(theme: "Theme"):
    return discord.Embed(
        title=f"Saved {theme.name} in your themes",
        description="View it in your themes with `/themes`"
    ).set_thumbnail(url=success_url(size=48))
