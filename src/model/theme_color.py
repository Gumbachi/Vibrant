from typing import Any

import discord

from .color import Color


class ThemeColor(Color):
    """Special Color class that keeps track of members for theme purposes."""

    def __init__(self, name: str, hexcode: str, members: list[int]):
        super().__init__(name, hexcode)
        self.members = members

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ThemeColor":
        return cls(
            name=data["name"],
            hexcode=data["hexcode"],
            members=data.get("members", [])
        )

    @classmethod
    def from_color(cls, color: Color, guild: discord.Guild) -> "ThemeColor":
        """Creates a ThemeColor from a normal Color."""
        return cls(
            name=color.name,
            hexcode=color.hexcode,
            members=[member.id for member in color.get_members(guild)]
        )

    def as_dict(self) -> dict[str, Any]:
        """Convert this color to a dict."""
        return {
            "name": self.name,
            "hexcode": self.hexcode,
            "members": self.members
        }

    def as_color(self) -> Color:
        """Convert this into a normal color."""
        return Color(
            name=self.name,
            hexcode=self.hexcode,
            role=self.role
        )
