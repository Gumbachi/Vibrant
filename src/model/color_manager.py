from __future__ import annotations

import discord
from cogs.color.components.colormenu import ColorMenu
from common.database import db
from utils.artist import draw_colors

from model.color import Color


class ColorManager:
    """Helps display and management of colors."""

    instances: dict[int, "ColorManager"] = {}

    def __init__(self, guild: discord.Guild):
        self.guild = guild
        self.colors = db.get_colors(guild.id)
        self.instances[guild.id] = self

    @property
    def snapshot(self):
        return draw_colors(self._colors)

    @property
    def controls(self):
        return ColorMenu(self)

    async def set_message(self, message: discord.Message) -> None:
        """Set the message and automatically delete the previous it"""
        if self._message != None:
            try:
                await self._message.delete()
            except discord.NotFound:
                return

        self._message = message

    def add_color(self, color: Color) -> bool:
        """Add a color to the color set."""
        success = db.add_color(id=self.guild.id, color=color)
        if success:
            self.colors.append(color)

        return success

    def remove_color(self, color: Color) -> bool:
        """Remove a color from the color set. Index is normalized"""
        success = db.remove_color(id=self.guild.id, color=color)
        if success:
            try:
                self.colors.remove(color)
            except ValueError:
                pass

    def find(self, search: str) -> Color | None:
        """Try to find color in list of colors. Returns None if nothing is found"""
        if search.isdigit():
            color = self._find_color_by_index(int(search))
            if color:
                return color

        color = self._find_color_by_name(search)
        return color

    def _find_color_by_index(self, index: int) -> Color | None:
        """!Index starting at 1!"""
        try:
            return self.colors[index - 1]
        except IndexError:
            return None

    def _find_color_by_name(self, name: str) -> Color | None:
        try:
            return next(c for c in self.colors if c.name == name)
        except StopIteration:
            return None

    def index_of(self, color: Color) -> int:
        """Find the index of a color by its name."""
        try:
            return self.colors.index(color) + 1
        except ValueError:
            return -1
