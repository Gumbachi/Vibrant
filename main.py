import os

from common.cfg import bot


@bot.listen()
async def on_ready():
    """Bot is ready to rumble."""
    print("Ready Player One.")


# Cogs the bot loads
extensions = [
    "cogs.general"
]

if __name__ == '__main__':
    for ext in extensions:
        try:
            bot.load_extension(ext)
            print(f"LOADED: {ext}")

        except Exception as e:
            print(f"Couldnt load {ext} because {e}")

bot.run(os.getenv("TOKEN"))  # runs the bot
