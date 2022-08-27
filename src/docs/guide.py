import discord

intro = discord.Embed(
    title="Vibrant Guide",
    description="Learn how to effectively use the bot",
).add_field(
    name="Table of contents",
    value="""
        2. Color Tutorial
        3. Theme/Preset Tutorial
        4. FAQ
    """
)

color_tutorial = discord.Embed(
    title="Colors Tutorial",
    description="How to manage and apply colors"
).add_field(
    name="Recommendation",
    value=("I recommend looking through all the commands the bot offers.\n"
           "Each command has a descriptions explaining what it does.\n"
           "Some commands also have optional arguments that change their behavior. You should also look at those."
           ),
    inline=False
).add_field(
    name="Add Some Colors",
    value=("View your colors with the `/colors` command.\n"
           "Add a color with the `/color add` command.\n"
           "View your new colors with the `/colors` command again. You can add up to 50 colors."
           ),
    inline=False
).add_field(
    name="Color People",
    value=("Apply a color to yourself with `/color me`.\n"
           "Apply your colors to the whole server with `/color splash`."
           ),
    inline=False
).add_field(
    name="Remove and Edit Colors",
    value=("Remove a color with `/color remove`.\n"
           "Edit a color name or value with `/color edit`. A new name or value must be provided\n"
           "If you want to remove all colors, use `/color clear`"
           ),
    inline=False
)

theme_tutorial = discord.Embed(
    title="Themes and Preset Tutorial",
    description="Want to save your current setup for later? Want to use some default presets?"
).add_field(
    name="Using Themes",
    value=("Save a theme with the `/theme save` command. This will remember your colors and who possessed them.\n"
           "Check saved themes with the `/themes` command.\n"
           "After the theme is saved you can safely use `/color clear`\n"
           "Recover the way your server was colored before by using `/theme apply`"
           ),
    inline=False
).add_field(
    name="Using Presets",
    value=("Presets are just pre-defined themes that anyone can use. Presets can be viewed with `/presets`\n"
           "You can use one of these presets by saving it with `/preset save` which will save it in your themes.\n"
           "Apply the theme with `/theme apply`."
           ),
    inline=False
)

FAQ = discord.Embed(
    title="Frequently Asked Questions"
).add_field(
    name="What to use for color value?",
    value=("The value is what defines how the color looks such as if it is Red, Green, or Blue\n"
           "Value can be either RGB or Hex format\n"
           "Use the value in the RGB or Hex field from [here (color picker)](https://htmlcolorcodes.com)"
           ),
    inline=False
).add_field(
    name="Why are my colors not showing up?",
    value=("When the bot creates roles it creates them at the bottom of the role hierarchy\n"
           "To have the color show, all of the roles above it need to be transparent colored"
           ),
    inline=False
).add_field(
    name="Why can't I see any commands",
    value=("The bot needs to have App Commands permission\n"
           "You can enable these permission by kicking and reinviting the bot to your server"
           ),
    inline=False
)


guide = [
    intro,
    color_tutorial,
    theme_tutorial,
    FAQ
]

for page in guide:
    page.add_field(
        name="---------------------------------",
        value="[Github](https://github.com/Gumbachi/Vibrant) • [Support Server](https://discord.gg/rhvyup5)",
        inline=False
    )
