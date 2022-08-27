import json
from pathlib import Path

import database as db
import discord
import utils
from cogs.theme.responses import MAX_THEMES_EMBED
from common.constants import MAX_THEMES
from discord import SlashCommandGroup, guild_only, option, slash_command
from model import Theme

from .responses import *


class PresetCog(discord.Cog):
    """Handles all of the preset related commands like preset save."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        preset_path = Path("src/resources/presets/")
        self.presets: list[Theme] = []

        for path in preset_path.glob("*.json"):
            with open(str(path)) as f:
                data = json.load(f)
                preset = Theme.from_dict(data=data)
            self.presets.append(preset)

    preset = SlashCommandGroup(
        name="preset",
        description="view and add presets with these commands."
    )

    async def preset_autocomplete(self, ctx: discord.AutocompleteContext):
        """Autocomplete preset names."""
        names = [preset.name for preset in self.presets]

        def ac_predicate(name: str) -> bool:
            name = name.lower()
            value = ctx.value.lower()
            return name.startswith(value) or value in name

        return [name for name in names if ac_predicate(name)]

    @slash_command(name="presets")
    async def display_presets(self, ctx: discord.ApplicationContext):
        """Display all of the presets vibrant has."""
        snapshots = utils.draw_themes(self.presets)
        await ctx.respond(files=snapshots)

    @preset.command(name="save")
    @guild_only()
    @option(name="preset", description="The preset to save to your themes", autocomplete=preset_autocomplete)
    async def save_preset(self, ctx: discord.ApplicationContext, preset: str):
        """Saves a preset to the themes of a guild."""
        theme = utils.find_by_name(name=preset, items=self.presets)
        if not theme:
            return await ctx.respond(embed=COULDNT_FIND_PRESET, ephemeral=True)

        themes = db.get_themes(id=ctx.guild.id)
        if len(themes) >= MAX_THEMES:
            await ctx.respond(embed=MAX_THEMES_EMBED, ephemeral=True)

        db.add_theme(id=ctx.guild.id, theme=theme)
        await ctx.respond(embed=preset_saved_embed(theme=theme))


def setup(bot: discord.Bot):
    bot.add_cog(PresetCog(bot))
