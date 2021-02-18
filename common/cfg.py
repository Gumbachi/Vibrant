"""Holds globals like the bot objects and extensions."""

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

emoji_dict = {"checkmark": "✅",
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
    128595549975871488,  # Gum
}

color_limit = 50
theme_limit = 10


def get_prefix(bot, message):
    """Gets the prefix per server"""
    return db.get(message.guild.id, "prefix")


bot = commands.Bot(command_prefix=get_prefix,
                   help_command=None)  # creates bot object

# none_embed = discord.Embed(
#     title="No active colors",
#     description=f"To add colors use the `add` command or import a theme",
#     color=discord.Color.blurple())
