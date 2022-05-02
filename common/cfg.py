"""Holds globals like the bot objects and extensions."""

import discord

intents = discord.Intents(
    members=True
)

bot = discord.Bot(
    description="Bot that manages roles based on Color",
    owner_id=128595549975871488,
    debug_guilds=[565257922356051973],
    activity=discord.Game("with colors"),
    intents=intents,
    status=discord.Status.dnd
)

emojis = {
    "checkmark": "✅",
    "crossmark": "❌",
    "left_arrow": "⬅️",
    "right_arrow": "➡️",
    "home_arrow": "↩️",
    "double_down": "⏬",
    "updown_arrow": "↕️",
}

color_limit = 50
theme_limit = 10
