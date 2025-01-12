import os

import discord

intents = discord.Intents.default()
intents.members = True

if os.getenv("DEBUG"):
    print("DEBUG ENVIRONMENT")
    bot = discord.Bot(
        description="Bot that manages roles based on Color",
        debug_guilds=[565257922356051973],
        activity=discord.Game("with colors"),
        intents=intents,
    )
else:
    print("LIVE ENVIRONMENT")
    bot = discord.Bot(
        description="Bot that manages roles based on Color",
        activity=discord.Game("with colors"),
        intents=intents,
    )


@bot.listen()
async def on_ready():
    """Executed when bot reaches ready state."""
    print("Ready Player One.")


# Cogs the bot loads
extensions = [
    "cogs.color.color_cog",
    "cogs.theme.theme_cog",
    "cogs.preset.preset_cog",
    "cogs.general.general_cog",  # General should come last
]


if __name__ == "__main__":
    bot.load_extensions(*extensions)

bot.run(os.getenv("TOKEN"))  # runs the bot
