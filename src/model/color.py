from dataclasses import dataclass, field

import discord
from PIL.ImageColor import getrgb


@dataclass(slots=True)
class Color:
    name: str
    hexcode: str
    roleid: int

    def __post_init__(self):
        if self.hexcode in ("#000", "#000000"):
            self.hexcode = "#010101"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data["name"],
            hexcode=data["hexcode"],
            role=data["role"],
        )

    @property
    def rgb(self):
        return getrgb(self.hexcode)

    @property
    def optimal_text_color(self) -> tuple:
        r, g, b = self.rgb
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return (0, 0, 0) if luminance > 0.5 else (240, 240, 240)

    def get_members(self, guild: discord.Guild) -> list[discord.Member]:
        """Fetch all the members with this color"""
        role = self.get_role(guild)
        return [] if not role else role.members

    def to_discord_color(self) -> discord.Colour:
        return discord.Colour.from_rgb(self.rgb)

    def get_role(self, guild: discord.Guild) -> discord.Role | None:
        """Fetch the role associated to this color or None if not found."""
        if self._role is None:
            return None

        return guild.get_role(self._role)
