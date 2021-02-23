"""Holds globals like the bot objects and extensions."""

import discord
from discord.ext import commands
from . import database as db

# Cogs the bot loads
extensions = [
    "cogs.admin",
    "cogs.errors",
    "cogs.general",
    "cogs.welcome",
    "cogs.color.info",
    "cogs.color.management",
    "cogs.color.assignment"
]

emojis = {"checkmark": "✅",
          "crossmark": "❌",
          "left_arrow": "⬅️",
          "right_arrow": "➡️",
          "home_arrow": "↩️",
          "up_arrow": "🔼",
          "down_arrow": "🔽",
          "double_down": "⏬",
          "refresh": "🔄",
          "updown": "↕️"}

admin_ids = {
    128595549975871488,  # me
}

color_limit = 50
theme_limit = 10

heavy_cmd = set()


def get_prefix(bot, message):
    """Gets the prefix per server"""
    return db.get(message.guild.id, "prefix")


intents = discord.Intents(guilds=True, members=True, messages=True)
bot = commands.Bot(command_prefix=get_prefix,
                   help_command=None, intents=intents)
