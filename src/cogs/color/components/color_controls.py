import discord

from .add_button import AddButton
from .refresh_button import RefreshButton


class ColorControls(discord.ui.View):
    def __init__(self):
        super().__init__(
            AddButton(),
            RefreshButton(),
            timeout=None
        )
