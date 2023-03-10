import database as db
import discord
import utils
from common.constants import MAX_THEMES
from discord import SlashCommandGroup, guild_only, option, slash_command
from model import Theme, ThemeColor

from .responses import *


class ThemeCog(discord.Cog):
    """Handles all of the theme related commands like theme apply."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    theme_commands = SlashCommandGroup(
        name="theme",
        description="save and manage themes with these commands",
        guild_only=True,
        default_member_permissions=discord.Permissions(manage_roles=True)
    )

    async def theme_autocomplete(self, ctx: discord.AutocompleteContext):
        """Autocomplete theme names."""
        themes = db.get_themes(id=ctx.interaction.guild.id)
        names = [theme.name for theme in themes]

        def ac_predicate(name: str) -> bool:
            name = name.lower()
            value = ctx.value.lower()
            return name.startswith(value) or value in name

        return [name for name in names if ac_predicate(name)]

    @slash_command(name="themes")
    @guild_only()
    async def display_themes(self, ctx: discord.ApplicationContext):
        """Display the themes the guild posesses."""
        themes = db.get_themes(id=ctx.guild.id)

        if not themes:
            return await ctx.respond(embed=NO_THEMES_EMBED, ephemeral=True)

        snapshots = utils.draw_themes(themes)
        await ctx.respond(files=snapshots)

    @theme_commands.command(name="save")
    @option(name="name", description="The name of the theme", min_length=1, max_length=99)
    @option(name="overwrite", description="The theme to overwrite", autocomplete=theme_autocomplete, required=False)
    async def save_theme(self, ctx: discord.ApplicationContext, name: str, overwrite: str):
        """Save the state of your colors in case you want to come back later."""
        colors = db.get_colors(guild_id=ctx.guild.id)

        if not colors:
            return await ctx.respond(embed=MISSING_COLORS_FOR_THEME, ephemeral=True)

        theme = Theme(
            name=name,
            colors=[ThemeColor.from_color(color, ctx.guild) for color in colors]
        )

        themes = db.get_themes(ctx.guild.id)

        # Save as new theme
        if not overwrite:

            if len(themes) >= MAX_THEMES:
                return await ctx.respond(embed=MAX_THEMES_EMBED, ephemeral=True)

            db.add_theme(ctx.guild.id, theme)

        else:

            # Overwriting a theme
            to_replace = utils.find_by_name(name=overwrite, items=themes)
            if not to_replace:
                return await ctx.respond(embed=COULDNT_FIND_THEME, ephemeral=True)

            # Replace old theme
            db.update_theme(id=ctx.guild.id, old=to_replace, new=theme)

        return await ctx.respond(embed=theme_saved_embed(theme))

    @theme_commands.command(name="remove")
    @option(name="theme", description="The theme to remove", autocomplete=theme_autocomplete)
    async def remove_theme(self, ctx: discord.ApplicationContext, theme: str):
        """Remove a theme from your themes"""
        themes = db.get_themes(ctx.guild.id)

        to_remove = utils.find_by_name(name=theme, items=themes)
        if not to_remove:
            return await ctx.respond(embed=COULDNT_FIND_THEME, ephemeral=True)

        db.remove_theme(id=ctx.guild.id, theme=to_remove)
        await ctx.respond(embed=remove_theme_sucess(theme=to_remove))

    @theme_commands.command(name="apply")
    @option(name="theme", description="The theme to apply", autocomplete=theme_autocomplete)
    @option(name="everyone", description="color people who dont have a color saved for this theme", default=True)
    async def apply_theme(self, ctx: discord.ApplicationContext, theme: str, everyone: bool):
        """Apply a saved theme to your server"""
        themes = db.get_themes(ctx.guild.id)

        # Find the theme
        theme_to_apply = utils.find_by_name(name=theme, items=themes)
        if not theme_to_apply:
            return await ctx.respond(embed=COULDNT_FIND_THEME, ephemeral=True)

        interaction = await ctx.respond(embed=REMOVING_PREVIOUS_THEME)

        # Should calculate roles and create then update database

        # Remove all colors
        colors = db.get_colors(ctx.guild.id)
        await utils.delete_color_roles(guild=ctx.guild, colors=colors)

        await interaction.edit_original_message(embed=APPLYING_THEME)
        await theme_to_apply.apply_to(guild=ctx.guild, include_everyone=everyone)

        db.replace_colors(
            id=ctx.guild.id,
            colors=[tc.as_color() for tc in theme_to_apply.colors]
        )

        return await interaction.edit_original_message(embed=theme_applied_embed(theme_to_apply))


def setup(bot: discord.Bot):
    bot.add_cog(ThemeCog(bot))
