import discord

MAX_COLORS = 50
MAX_THEMES = 10

NO_COLORS_EMBED = discord.Embed(title="You have no colors :(")
MAX_COLORS_EMBED = discord.Embed(
    title=f"Maximum Colors Reached ({MAX_COLORS})",
    color=discord.Colour.red()
)
MAX_THEMES_EMBED = discord.Embed(
    title=f"Maximum Themes Reached ({MAX_THEMES})",
    color=discord.Colour.red()
)

INVALID_HEXCODE = discord.Embed(
    title="Invalid hexcode",
    description="[Learn More](https://htmlcolorcodes.com)"
)

ADD_COLOR_UNSUCCESSFUL = discord.Embed(
    title="Could not add color",
    color=discord.Colour.red()
)
