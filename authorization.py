"""Defines some custom functions and an authorization function to
improve readability in commands."""

import re
import discord
from discord.ext.commands import CommandError, UserInputError

from classes import Guild
from vars import heavy_command_active, preset_names


class MissingGuild(CommandError):
    """Error for not finding a guild"""
    pass


class MissingPermissions(CommandError):
    """Error for not having proper permissions"""
    pass


class ChannelDisabled(CommandError):
    """Raise for a disabled channel"""
    pass


class NoAvailableColors(CommandError):
    """Raised when there are no colors available"""
    pass


class NoAvailableThemes(CommandError):
    """Raised when there are no colors available"""
    pass


class HeavyCommandActive(CommandError):
    """Raised when there is a heavy command like splash active"""
    pass


class LimitReached(CommandError):
    """Raised when a color/theme limit is reached."""
    pass


class InvalidHexcode(UserInputError):
    """Raised for invalid hexcode."""
    pass


class InvalidName(UserInputError):
    """Raised when color/theme name is improper."""
    pass


class NotFoundError(UserInputError):
    """Raised when color cannot be found with a given string/threshold"""
    pass


class UserMissingColorRole(CommandError):
    """Raised when user does not have color role"""
    pass


class InvalidSwapQuery(UserInputError):
    """Raised when a swap query for rename or recolor is invalid"""
    pass


def is_disabled(channel):
    """Evaluate if a discord channel is disabled."""
    return (isinstance(channel, discord.DMChannel)
            or channel.id in Guild.get(channel.guild.id).disabled_channel_ids)


def authorize(ctx, *checks, **input_checks):
    """Check certain perms and assure passing."""

    # Guild related checks
    guild = Guild.get(ctx.guild.id)

    if not guild:
        raise MissingGuild()

    ############## GENERAL COMMAND EXCEPTIONS ##############

    # Channel related checks
    if "disabled" in checks and ctx.channel.id in guild.disabled_channel_ids:
        raise ChannelDisabled()

    # Permission related checks
    if "roles" in checks and not ctx.author.guild_permissions.manage_roles:
        raise MissingPermissions("Manage Roles")

    if "server" in checks and not ctx.author.guild_permissions.manage_guild:
        raise MissingPermissions("Manage Server")

    if "channels" in checks and not ctx.author.guild_permissions.manage_channels:
        raise MissingPermissions("Manage Channels")

    # Command related checks
    if "heavy" in checks and ctx.guild.id in heavy_command_active:
        raise HeavyCommandActive(heavy_command_active[ctx.guild.id])

    # Color related checks
    if "colors" in checks and not guild.colors:
        raise NoAvailableColors()

    if "color_limit" in checks and len(guild.colors) >= guild.color_limit:
        raise LimitReached("colors")

    # Theme related checks
    if "themes" in checks and not guild.themes:
        raise NoAvailableThemes()

    if "theme_limit" in checks and len(guild.themes) >= guild.theme_limit:
        raise LimitReached("themes")

    ############## USER INPUT EXCPETIONS ##############

    if "name" in input_checks:
        name = input_checks["name"]

        # check for separator bar
        if re.search(r"[|]+", name):
            raise InvalidName(
                "Names cannot include `|`")

        if 100 < len(name) < 1:
            raise InvalidName(
                "Names must be between 1-100 characters")

    if "hexcode" in input_checks:
        hexcode = input_checks["hexcode"]
        if not bool(re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', hexcode)):
            raise InvalidHexcode(hexcode)

    if "color_query" in input_checks:
        query, threshold = input_checks["color_query"]
        if not bool(guild.find_color(query, threshold)):
            raise NotFoundError(query)

    if "theme_query" in input_checks:
        query, threshold = input_checks["theme_query"]
        if not bool(guild.find_theme(query, threshold)):
            raise NotFoundError(query)

    if "user_query" in input_checks:
        query, threshold = input_checks["user_query"]
        if not bool(guild.find_user(query, ctx.message, threshold)):
            raise NotFoundError(query)

    if "preset_query" in input_checks:
        preset = input_checks["preset_query"]
        if preset not in preset_names:
            raise NotFoundError(preset)

    if "has_color" in input_checks:
        if not guild.get_color_role(input_checks["has_color"]):
            raise UserMissingColorRole()

    if "swap_query" in input_checks:
        query = input_checks["swap_query"]
        if not re.search(r"[\d\w\s]+[|]{1}[\d\w\s]+", input_checks["swap_query"]):
            raise InvalidSwapQuery("Invalid Input.")

        try:
            _, _ = query.split("|")
        except ValueError:
            raise InvalidSwapQuery(
                f"There are too many separators in **{query}**.")

    return True
