from dbl import DBLClient
import discord
from discord.ext import commands
from vars import bot
from cfg import apikey

class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = apikey
        self.dblpy = DBLClient(self.bot, self.token, autopost=True) # Autopost will post your guild count every 30 minutes

def setup(bot):
    bot.add_cog(TopGG(bot))