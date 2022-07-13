import enum
from dataclasses import dataclass, field

import discord
from cogs.color.components import ColorMenu
from common.database import db
from model.color import Color
from utils.artist import draw_colors


@dataclass(slots=True)
class ColorManager:
    """Allows display and management of colors."""

    id: int
    colors: list[Color]
    message: discord.Message

    @property
    def snapshot(self):
        return draw_colors(self._colors)

    @property
    def controls(self):
        return ColorMenu(self)

    async def set_message(self, message: discord.Message):
        """Set the message and automatically delete the previous it"""
        if self._message != None:
            try:
                await self._message.delete()
            except discord.NotFound:
                return

        self._message = message

    def add_color(self, color: Color):
        """Add a color to the color set."""
        success = db.add_color()
        if success:
            self.colors.append(color)

        return success

    def remove_color(self, index: int):
        """Remove a color from the color set."""
        try:
            self.colors.pop(index - 1)
        except IndexError:
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

    # def find_color_index(self, name: str) -> int:
    #     """Find the index of a color by its name."""
    #     for i, color in enumerate(self.colors, 1):
    #         if color.name == name:
    #             return i
    #     return -1
