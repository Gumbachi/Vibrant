import asyncio
import random
from dataclasses import dataclass
from itertools import cycle

import discord

from .theme_color import ThemeColor


@dataclass(slots=True)
class Theme:
    name: str
    colors: list[ThemeColor]

    @classmethod
    def from_dict(cls, data: dict):
        """Create a Theme from a dict."""
        return cls(
            name=data["name"],
            colors=[ThemeColor.from_dict(data=color) for color in data["colors"]]
        )

    def as_dict(self):
        """Serialize/Convert theme into a dict for json database."""
        return {
            "name": self.name,
            "colors": [tc.as_dict() for tc in self.colors]
        }

    async def apply_to(self, guild: discord.Guild, include_everyone: bool = False):
        """Apply a theme to a provided guild."""

        uncolored = guild.members

        for color in self.colors:
            for member_id in color.members:
                member = guild.get_member(member_id)
                if member:
                    await color.apply_to(target=member, updatedb=False)
                    await asyncio.sleep(1)
                    uncolored.remove(member)

        # shuffle is in-place
        shuffled = self.colors
        random.shuffle(shuffled)

        if include_everyone:
            for color, member in zip(cycle(shuffled), uncolored):
                await color.apply_to(target=member, updatedb=False)
                await asyncio.sleep(1)
