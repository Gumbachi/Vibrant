import re
from typing import Generator

import discord

import model
from utils.errors import InvalidColorValue


def is_valid_hex(hexcode: str) -> bool:
    """Validate a hex code."""
    return bool(re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', hexcode))


def fetch_color_roles(guild: discord.Guild, colors: list[model.Color]) -> Generator[discord.Role, None, None]:
    """Fetches the roles in the guild that correspond to a color"""
    color_ids = {color.role_id for color in colors if color.role_id is not None}
    return (role for role in guild.roles if role.id in color_ids)


def is_color_role(role: discord.Role, colors: list[model.Color]) -> bool:
    """Check if a role is associated with a color in the list of colors"""
    color_ids = {color.role_id for color in colors if color.role_id is not None}
    return role.id in color_ids


def find_color_by_role_id(id: int, colors: list[model.Color]) -> model.Color | None:
    """Find a color by its role id."""
    return next((c for c in colors if c.role_id == id), None)


def get_colors_from_person(person: discord.Member, colors: list[model.Color]):
    """Determine the colors a person is holding."""
    role_ids = [role.id for role in person.roles]
    return [c for c in colors if c.role_id in role_ids]


async def delete_color_roles(guild: discord.Guild, colors: list[model.Color]):
    """Delete all color roles."""
    for role in fetch_color_roles(guild=guild, colors=colors):
        await role.delete()


def parse_string_to_hex(value: str) -> str:
    """Convert a string to valid hex or raise error"""

    # valid hex
    if is_valid_hex(hexcode=value):
        return value

    # parse RGB
    values = re.findall(pattern=r"\d?\d?\d", string=value)
    values = [int(val) for val in values]

    if len(values) != 3 or not all([0 <= val <= 255 for val in values]):
        raise InvalidColorValue()

    r, g, b = [int(value) for value in values]
    return f"#{r:02x}{g:02x}{b:02x}"


def parse_color_or_none(value: str) -> str | None:
    """Convert a string to valid hex or return None"""

    # valid hex
    if is_valid_hex(hexcode=value):
        return value

    # parse RGB
    values = re.findall(pattern=r"\d?\d?\d", string=value)
    values = [int(val) for val in values]

    if len(values) != 3 or not all([0 <= val <= 255 for val in values]):
        return None

    r, g, b = [int(value) for value in values]
    return f"#{r:02x}{g:02x}{b:02x}"
