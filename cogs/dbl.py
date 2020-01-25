import os

import discord
from dbl import DBLClient
from discord.ext import commands

from vars import bot


class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = os.environ["DBL_API_KEY"]
        # Autopost will post your guild count every 30 minutes
        self.dblpy = DBLClient(self.bot, self.token, autopost=True)


def setup(bot):
    bot.add_cog(TopGG(bot))
