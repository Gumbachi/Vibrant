import os

import discord
import common.cfg as cfg
from common.cfg import bot


@bot.event
async def on_ready():
    """Change presence and report ready."""
    activity = discord.Game(name=f"@Vibrant for help ({len(bot.guilds)})")
    await bot.change_presence(activity=activity)
    print("Ready Player One.")


@bot.event
async def on_message(message):
    """Message listener."""
    # make sure it doesnt run when bot writes message
    if message.author == bot.user:
        return

    # shows prefix if bot is mentioned
    if message.mentions and message.mentions[0].id == bot.user.id:
        return await message.channel.send(
            f"Type `{cfg.get_prefix(bot, message)}`help for help.")

    await bot.process_commands(message)

# loads extensions(cogs) listed in cfg.py
if __name__ == '__main__':
    for extension in cfg.extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f"Couldnt load {extension}")
            print(e)

bot.run(os.getenv("TOKEN"))  # runs the bot
