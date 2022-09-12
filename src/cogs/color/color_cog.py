import asyncio
import random
from itertools import cycle

import database as db
import discord
import utils
from discord import (SlashCommandGroup, guild_only, option, slash_command,
                     user_command)
from model import Color

from .components import ColorControls
from .responses import *


class ColorCog(discord.Cog):
    """Handles all of the color related commands like color me."""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    color = SlashCommandGroup(
        name="color",
        description="commands to create and manage colors",
        guild_only=True,
        default_member_permissions=discord.Permissions(manage_roles=True)
    )

    async def autocomplete_color(ctx: discord.AutocompleteContext):
        """General use autocomplete for looking for a specific color."""
        colors = db.get_colors(ctx.interaction.guild.id)
        names = [color.name for color in colors]

        def ac_predicate(name: str) -> bool:
            name = name.lower()
            value = ctx.value.lower()
            return name.startswith(value) or value in name

        return [name for name in names if ac_predicate(name)]

    @slash_command(name="colors")
    @guild_only()
    async def display_colors(self, ctx: discord.ApplicationContext):
        """Display the servers current colors."""
        colors = db.get_colors(ctx.guild.id)

        if not colors:
            return await ctx.respond(embed=NO_COLORS_EMBED, ephemeral=True)

        snapshot = utils.draw_colors(colors)
        await ctx.respond(file=snapshot, view=ColorControls())

    @slash_command(name="colorme")
    @guild_only()
    @option(name="color", description="The color to apply.", autocomplete=autocomplete_color)
    async def color_author(self, ctx: discord.ApplicationContext, color: str):
        """Color yourself your favorite color."""
        for cmd in self.color.walk_commands():
            if cmd.qualified_name == "color them":
                await ctx.invoke(cmd, ctx.author, color)

    @user_command(name="Color Randomly")
    @guild_only()
    async def color_randomly(self, ctx: discord.ApplicationContext, member: discord.Member):
        """Color the selected person a random color"""
        colors = db.get_colors(id=ctx.guild.id)

        if not colors:
            return await ctx.respond(embed=NO_COLORS_EMBED, ephemeral=True)

        new_color = random.choice(colors)

        # Remove any previous colors
        owned_colors = utils.get_colors_from_person(person=member, colors=colors)
        for owned_color in owned_colors:
            await owned_color.remove_from(member)

        # add New color
        await new_color.apply_to(member)
        await ctx.respond(embed=color_applied_embed(new_color, member))

    @color.command(name="them")
    @option(name="target", description="The person to be colored")
    @option(name="color", description="The color to apply", autocomplete=autocomplete_color)
    async def color_someone(
        self, ctx: discord.ApplicationContext,
        target: discord.Member,
        color: str
    ):
        """Color someone else your favorite color."""
        # Attempt to find color
        colors = db.get_colors(id=ctx.guild.id)

        if not colors:
            return await ctx.respond(embed=NO_COLORS_EMBED, ephemeral=True)

        new_color = utils.find_by_name(name=color, items=colors)
        if not new_color:
            return await ctx.respond(embed=COULDNT_FIND_COLOR, ephemeral=True)

        # Remove any previous colors
        owned_colors = utils.get_colors_from_person(person=target, colors=colors)
        for owned_color in owned_colors:
            await owned_color.remove_from(target)

        # add New color
        await new_color.apply_to(target)
        await ctx.respond(embed=color_applied_embed(new_color, target))

    @color.command(name="add")
    @option(name="name", description="The name for your new color")
    @option(name="value", description="The value of the color (Hex or RGB). Example: '#7289DA'")
    async def add_color(
        self, ctx: discord.ApplicationContext,
        name: str,
        value: str
    ):
        """Add your favorite color."""
        # Check color limit
        colors = db.get_colors(ctx.guild.id)
        if len(colors) >= MAX_COLORS:
            return await ctx.respond(embed=MAX_COLORS_EMBED, ephemeral=True)

        color = Color(name=name, hexcode=value, role=None)
        db.add_color(ctx.guild.id, color)

        await ctx.respond(embed=add_color_success(color))

    @color.command(name="remove")
    @option(name="color", description="The color to remove", autocomplete=autocomplete_color)
    async def remove_color(self, ctx: discord.ApplicationContext, color: str):
        """Remove your favorite color."""
        colors = db.get_colors(ctx.guild.id)
        color_to_remove = utils.find_by_name(name=color, items=colors)

        if not color_to_remove:
            return await ctx.respond(embed=COULDNT_FIND_COLOR, ephemeral=True)

        await color_to_remove.erase(guild=ctx.guild)
        db.remove_color(ctx.guild.id, color_to_remove)
        await ctx.respond(embed=remove_color_success(color_to_remove))

    @color.command(name="splash")
    @option(name="type", description="The type of splash to perform.", choices=["Default", "Resplash", "Unsplash"], default="Default")
    async def splash_color(self, ctx: discord.ApplicationContext, type: str):
        """Color everyone that is uncolored. Or uncolor everyone. Or recolor everyone."""
        colors = db.get_colors(ctx.guild.id)

        if not colors and type != "Unsplash":
            return await ctx.respond(embed=NO_COLORS_EMBED, ephemeral=True)

        interaction = await ctx.respond(embed=GETTING_THINGS_READY)

        # Unsplash Operation
        if type in ("Unsplash", "Resplash"):
            await utils.delete_color_roles(guild=ctx.guild, colors=colors)

            if type == "Unsplash":
                return await interaction.edit_original_message(embed=UNSPLASH_SUCCESS)

        await interaction.edit_original_message(embed=SPLASH_COLORING_PEOPLE)

        # randomize colors and member order
        random.shuffle(colors)
        uncolored = [m for m in ctx.guild.members if not utils.get_colors_from_person(m, colors)]
        random.shuffle(uncolored)

        for color, member in zip(cycle(colors), uncolored):
            await color.apply_to(member)
            await asyncio.sleep(1)

        # Sleep to ensure message is updated if the bot has little processing to do
        if not uncolored:
            await asyncio.sleep(1)

        await interaction.edit_original_message(embed=splash_successful(amount=len(uncolored)))

    @color.command(name="clear")
    async def clear_colors(self, ctx: discord.ApplicationContext):
        """WARNING: Clears all colors and uncolors everyone with a color."""
        colors = db.get_colors(ctx.guild.id)

        if not colors:
            return await ctx.respond(embed=NO_COLORS_EMBED, ephemeral=True)

        interaction = await ctx.respond(embed=REMOVING_COLORS)

        await utils.delete_color_roles(guild=ctx.guild, colors=colors)

        db.replace_colors(id=ctx.guild.id, colors=[])
        await interaction.edit_original_message(embed=CLEAR_COLORS_SUCCESS)

    @color.command(name="edit")
    @option(name="color", description="The color to edit", autocomplete=autocomplete_color)
    @option(name="name", description="The new name for the color", required=False)
    @option(name="value", description="The new value for your color (hex or RGB)", required=False)
    async def edit_color(
        self, ctx: discord.ApplicationContext, color: str,
        name: str,
        value: str
    ):
        """Edit a color's name or value."""
        colors = db.get_colors(ctx.guild.id)
        uneditied_color = utils.find_by_name(name=color, items=colors)

        if not uneditied_color:
            return await ctx.respond(embed=COULDNT_FIND_COLOR, ephemeral=True)

        if not name and not value:
            return await ctx.respond(embed=MISSING_EDIT_INFO, ephemeral=True)

        # default values if value not provided
        name = name if name else uneditied_color.name
        value = value if value else uneditied_color.hexcode

        # create the new color
        edited_color = Color(name=name, hexcode=value, role=uneditied_color.role)

        # Edit the associated role
        if (role := await uneditied_color.get_role(ctx.guild)):
            # This edit will automatically update the database because of event listener
            await role.edit(name=name, color=edited_color.to_discord_color())

        await ctx.respond(embed=edit_successful(uneditied_color, edited_color))

    @discord.Cog.listener(name="on_guild_role_update")
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        """Listener to keep roles and colors in sync if changed from discord client."""
        if before.name == after.name and before.color == after.color:
            return

        colors = db.get_colors(before.guild.id)
        if (old_color := utils.find_color_by_role_id(id=before.id, colors=colors)):
            new_color = Color(after.name, hexcode=str(after.color), role=after.id)
            db.update_color(before.guild.id, old_color, new_color)

    @discord.Cog.listener(name="on_application_command_error")
    async def on_application_command_error(self, ctx: discord.ApplicationContext, exception: discord.ApplicationCommandInvokeError):
        """Error handler for all these color commands."""

        if hasattr(exception, "original"):
            error = exception.original
        else:
            error = exception

        if isinstance(error, utils.errors.InvalidColorValue):
            return await ctx.respond(embed=INVALID_COLOR_VALUE, ephemeral=True)

        if isinstance(error, utils.errors.InvalidColorName):
            return await ctx.respond(embed=INVALID_COLOR_NAME, ephemeral=True)

        # Invalidate Caches For Guild
        try:
            del db.color.color_cache[ctx.guild.id]
            del db.theme.theme_cache[ctx.guild.id]
        except KeyError:
            pass

        if ctx.response.is_done():
            await ctx.interaction.edit_original_message(embed=error_embed(error))
        else:
            await ctx.respond(embed=error_embed(error), ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(ColorCog(bot))
