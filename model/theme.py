import random
from discord import Color


class Theme:
    def __init__(self):
        self.colors: list[Color] = []

    @property
    def empty(self):
        """True if there are no colors"""
        return len(self.colors) == 0

    def random_color(self):
        """Get a random color from the theme."""
        return random.choice(self.colors)
