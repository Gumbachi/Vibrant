"""Holds globals like the bot objects and extensions"""

import discord
from discord.ext import commands

# Cogs the bot loads
extensions = [
    # General
    "cogs.basic",
    "cogs.channels",
    "cogs.errors",
    "cogs.utility",
    "cogs.dbl",

    # Color
    "cogs.color.color_assignment",
    "cogs.color.color_info",
    "cogs.color.color_management",

    # Theme
    "cogs.theme.theme_assignment",
    "cogs.theme.theme_info",
    "cogs.theme.theme_management",
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


def get_prefix(bot, message):
    """Gets the prefix per server"""
    return "$"
    # if isinstance(message.channel, discord.channel.DMChannel):
    #     return
    # else:
    #     id = message.guild.id

    # try:
    #     data = db.coll.find_one({"id": id})
    # except:
    #     print("no coll found for prefix")
    #     return '$'
    # if not data:
    #     return '$'
    # if "prefix" not in data.keys():
    #     data["prefix"] = '$'
    # return data["prefix"]


bot = commands.Bot(command_prefix=get_prefix,
                   help_command=None)  # creates bot object

none_embed = discord.Embed(
    title="No active colors",
    description=f"To add colors use the `add` command or import a theme",
    color=discord.Color.blurple())
