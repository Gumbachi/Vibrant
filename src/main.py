import os

import discord

from model.color_manager import ColorManager

bot = discord.Bot(
    description="Bot that manages roles based on Color",
    owner_id=128595549975871488,
    debug_guilds=[565257922356051973],
    activity=discord.Game("with colors"),
    status=discord.Status.dnd,
    intents=discord.Intents(members=True),
)


@bot.listen()
async def on_ready():
    """Executed when bot reaches ready state."""
    for guild in bot.guilds:
        ColorManager(guild)

    print("Ready Player One.")


# Cogs the bot loads
extensions = ["cogs.general", "cogs.color.color"]

if __name__ == "__main__":
    for ext in extensions:
        try:
            bot.load_extension(ext)
            print(f"LOADED: {ext}")

        except Exception as e:
            print(f"Couldnt load {ext} because {e}")

bot.run(os.getenv("TOKEN"))  # runs the bot
