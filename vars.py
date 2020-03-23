import discord
from discord.ext import commands
import database as db

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
              "crossmark": "❌"}

preset_names = [
    "basic",
    "vibrant",
    "rainbow",
    "metro",
    "icecream",
    "neon",
    "pastel",
    "outrun",
    "sunset",
    "discord",
    "christmas",
]


def get_prefix(bot, message):
    """Gets the prefix per server"""
    if isinstance(message.channel, discord.channel.DMChannel):
        for guild in bot.guilds:
            if guild.get_member(message.author.id) is not None:
                id = guild.id
    else:
        id = message.guild.id

    try:
        data = db.coll.find_one({"id": id})
    except:
        print("no coll found for prefix")
        return '$'
    if not data:
        return '$'
    if "prefix" not in data.keys():
        data["prefix"] = '$'
    return data["prefix"]


bot = commands.Bot(command_prefix=get_prefix,
                   help_command=None)  # creates bot object

none_embed = discord.Embed(
    title="No active colors",
    description=f"To add colors use the `add` command or import a theme",
    color=discord.Color.blurple())

disabled_embed = discord.Embed(
    title="Channel is Disabled", description=f"The channel you tried to use is disabled")


def get_help(p):
    return {
        "Help": {
            "1. Setup": "Shows you how to set up the bot easily and how to use basic commands",
            "2. Themes": "Learn how to use themes",
            "3. General Commands": "Shows a list of general commands the bot has",
            "4. Color Commands": "Shows a list of color related commands the bot has",
            "5. Theme Commands": "Shows a list of theme related commands the bot has",
            "-----------------------------": "[Vote for Vibrant](https://top.gg/bot/589685258841096206/vote) | [Support Server](https://discord.gg/rhvyup5) | [Github](https://github.com/Gumbachi/Vibrant) | [Report an issue](https://github.com/Gumbachi/Vibrant/issues)"
        },
        "Setup": {
            "Add Custom Color": f"""-add a custom color by typing `{p}add #ff0000 My Color`
                                  -Add a few more colors if you'd like using `{p}add` and view them by typing `{p}colors`""",
            "Setting Themes": f"""Learn how to save your colors, use presets and hot swap the way your server looks by using themes. Type `{p}help themes`""",
            "Coloring People": f"""-Color yourself by typing `{p}colorme` This will assign you a random color. To get a specific color type `{p}colorme <index/color>`
                                   -Color others by typing `{p}color <user>` This will try to find a user and assigning a random color. To get a specific color type `{p}color <user> <index/color>`
                                   -Color everyone that isn't colored by typing `{p}splash`. This command may take some time depending on the amount of members who are uncolored""",
            "Change Colors": f"""-Change the name of a color by typing `{p}rename <index/color> | <new name>`
                                 -Change the look of a color by typing `{p}recolor <index/color> | <new hexcode>`
                                 -[Color Picker](https://www.google.com/search?q=color+picker)""",
            "Remove Colors": f"""-Remove a color by typing `{p}remove <index/color>`
                                 -Remove all colors by typing `{p}clear_all_colors`. This is made difficult to type on purpose""",
            "Set a Welcome Channel": f"""-Set a welcome channel for the bot to send a message in the channel when ever a new person joins your server
                                         -Go to your desired channel and type `{p}welcome` to set it as the welcome channel
                                         -This can be reverted by typing `{p}welcome remove`""",
            "Disable/Enable Channels": f"""-Disable a channel by typing `{p}disable` in the desired channel
                                           -Enable a channel by typing `{p}enable` in the desired channel
                                           -If you want to disable/enable all channels then type `{p}disable all` or `{p}enable all` in any channel""",
        },
        "Themes": {
            "Importing Themes": f"""Import a preset theme by using `{p}import vibrant`.
                                    This will import a preset called "Vibrant"
                                    After importing, color everyone with `{p}splash`.""",
            "Managing your Themes": f"""Add a custom color by typing `{p}add #ffffff White`
                                        You can save this new preset by typing `{p}theme.save My Custom Theme`
                                        Remove your first theme by using `{p}theme.remove 1` or `{p}t.r 1`
                                        Load your custom theme by typing `{p}theme.load 1` or `{p}t.l 1`
                                        If you want to replace one theme with another then use `{p}theme.overwrite <index/name> | <name of new theme>` or `{p}t.o` for short.
                                        If you would like to rename your theme then do so by using `{p}theme.rename` or `{p}t.rn`. For more help on this command type `{p}help theme.rename`.""",
            "Viewing your themes": f"""View all of your themes by typing `{p}themes` or `{p}t`."""
        },
        "Commands": {
            "General Commands": f"""`{p}howdy`: You've got a friend in me
                                    `{p}prefix <new prefix>`: changes the prefix the bot uses
                                    `{p}report <issue>`: sends a message to the developer with your problem
                                    """,
            "Channel Commands": f"""`{p}enable <all>`: Enables the channel or all channels
                                    `{p}disable <all>`: Disables the channel or all channels
                                    `{p}welcome <remove>`: Toggles the channel for greeting users
                                    `{p}status`: displays disabled/enabled status for channel
                                    `{p}channels`: Shows disabled channels and welcome channel
                                    """
        },
        "Color Commands": {
            "Color Commands": f"""`{p}colorme <name/index>`: Gives you your desired color or a random one
                                  `{p}color <user> <name/index>`: Gives a specific user a color
                                  `{p}colors`: Shows available colors
                                  `{p}add <hexcode> <name>`: Adds a color to the palette
                                  `{p}remove <name/index>`: Removes a color from the palette
                                  `{p}rename <name/index> | <new name>`: Changes a color's name
                                  `{p}recolor <name/index> | <new hexcode>`: Changes a color's value
                                  `{p}splash`: Gives a color to everyone in the server without one
                                  `{p}unsplash`: Uncolors everyone
                                  `{p}info <name/index>`:shows info about a color
                                """
        },
        "Theme Commands": {
            "Theme Commands": f"""`{p}themes`: Draws a pretty list of themes
                                  `{p}theme.save <name>`: Saves your theme
                                  `{p}theme.remove <name/index>`: Deletes a theme
                                  `{p}theme.overwrite <name/index> | <name of new theme>`: Replaces a theme
                                  `{p}theme.load <name/index>`: Applies a saved theme to your server
                                  `{p}theme.rename <name/index> | <new name>`: Changes a theme's name
                                  `{p}theme.info <name/index>`: Shows info about a given theme
                                  `{p}import <name>`: Adds a preset as a theme
                                """
        },
    }


def get_commands(p):
    return {
        "help": {
            "Description": "Do you really need one?",
            "Usage": f"`{p}help`: You know what this does",
        },
        "howdy": {
            "Description": "A friendly function that replies howdy",
            "Usage": f"`{p}howdy`",
        },
        "colorme": {
            "Description": "Will give you a color if there are any",
            "Arguments": "`name/index`: Optional field where you can input a specific color index or name to get a specific color",
            "Usage": f"`{p}colorme`: Colors you a random color\n`{p}colorme blue`: Colors you blue if the color exists\n`{p}colorme 2`: Colors you whatever color is in the 2nd slot of the set",
            "Aliases": f"`{p}colourme`, `{p}me`",
        },
        "color": {
            "Description": "Colors another user",
            "Arguments": "`user`: this is a required field where you can @mention a user or type in their name to find a user\n`color/index`: this is an optional field where you can input a specific color index or name to get a specific color",
            "Usage": f"`{p}color @gumbachi`: Colors the mentioned user a random color\n`{p}color @gumbachi 2`: colors the mentioned user the 2nd color\n`{p}color Gumbachi blue`",
            "Aliases": f"`{p}colour`, `{p}cu`",
        },
        "colors": {
            "Description": "Generates an image of all the colors and sends it",
            "Usage": f"`{p}colors`",
            "Aliases": f"{p}`colours`, `{p}c`",
        },
        "splash": {
            "Description": "Colors everyone without a color in the server",
            "Usage": f"`{p}splash`",
            "More Info": """Takes time because discord's API puts a limit on how many actions can be performed."""
        },
        "unsplash": {
            "Description": "Removes everyone's colors",
            "Usage": f"`{p}unsplash`",
            "More Info": """Takes time because discord's API puts a limit on how many actions can be performed."""
        },
        "add": {
            "Description": "Adds a custom color to the colorset",
            "Arguments": """`hexcode`: Required field where you can input a hexcode for your desired color
                         `name`: Optional field for the name of your new color""",
            "Usage": f"`{p}add #ff0000 Red`: Adds a color named red to the set\n`{p}add #ffff00`:Adds a color named 'Color x' to the set",
            "Aliases": f"`{p}new`, `{p}a`",
            "More Info": "Will give the color a name like 'Color 2' if name field left blank"
        },
        "enable": {
            "Description": "Enables the channel it is typed in",
            "Arguments": """`all`: Optional field where you can type all to specify if you want all channels enabled""",
            "Usage": f"`{p}enable`: enable just this channel\n`{p}enable all`: enable all channels"
        },
        "remove": {
            "Description": "Removes a color from the colorset",
            "Arguments": "`color/index`: Required field where you can input a color name or index for your desired color",
            "Usage": f"`{p}remove Red`: Will try to remove a color named red\n`{p}remove 3`: Removes the color in the 3rd slot",
            "Aliases": f"`{p}delete`, `{p}r`"
        },
        "rename": {
            "Description": "Renames a color in the colorset",
            "Arguments": """`color/index`: this is a required field where you can type a color name or index to change
                         `new name`: this is a required field for the new name of the color""",
            "Usage": f"`{p}rename blue | red`: Will rename a color named blue to red\n`{p}rename 4 | Blue`: Renames the 4th color to Blue",
            "More Info": "Uses a `|` separator to split the before and after",
            "Aliases": f"`{p}rn`"
        },
        "recolor": {
            "Description": "Changes a color's look",
            "Arguments": """`color/index`: this is a required field where you can type a color name or index to change
                         `new hexcode`: this is a required field for the new hexcode of the color""",
            "Usage": f"`{p}recolor blue | #0000ff`: Will change the value of blue to #0000ff(blue)\n`{p}recolor 4 | #ffffff`: Changes the value of the 4th color to #ffffff(white)",
            "Aliases": f"`{p}recolour`, `{p}rc`",
            "More Info": """Uses a `|` separator to split the before and after"""
        },
        "prefix": {
            "Description": "Changes the server prefix",
            "Arguments": """`new prefix`: this is a required field for the new prefix""",
            "Usage": f"`{p}prefix $`: Will change prefix to $\n`{p}vibrantprefix $`: Does the same thing under a different alias",
            "Aliases": "`vibrantprefix`",
            "More Info": f"if you have overlap issues then use `{p}vibrantprefix` to dodge command overlap"
        },
        "clear_all_colors": {
            "Description": "Will remove all colors from a colorset",
            "Usage": f"`{p}clear_all_colors`",
            "Aliases": "`clear_all_colours`",
            "More Info": "Is made difficult on purpose to avoid accidents"
        },
        "channels": {
            "Description": "Sends channel information",
            "Usage": f"`{p}channels`",
        },
        "version": {
            "Description": "Sends a message containing patch notes",
            "Arguments": "`version`:  optional for the version you want to see",
            "Usage": f"`{p}version`: Sends latest\n`{p}version 1.4`: sends v1.4 notes",
        },
        "import": {
            "Description": "Imports a theme from from a preset",
            "Arguments": "`name`: The name of the preset you want to import",
            "Usage": f"`{p}import vibrant`: Imports the vibrant preset as a theme",
        },
        "disable": {
            "Description": "Disables the channel it is typed in",
            "Arguments": "`all`:  optional field where you can type all to specify if you want all channels disabled",
            "Usage": f"`{p}disable`: disable just this channel\n`{p}disable all`: disable all channels"
        },
        "report": {
            "Description": "Sends a message to me(Gumbachi). you can just say 'Hi' if you want to:).",
            "Arguments": "`message`: this is a required containing your message",
            "Usage": f"`{p}report Hi Gum`: Sends 'Hi Gum' to me",
            "More Info": "Support Server: https://discord.gg/rhvyup5"
        },
        "status": {
            "Description": "Sends a message saying if the channel is enable or not",
            "Usage": f"`{p}status`"
        },
        "welcome": {
            "Description": "Sets or removed the welcome channel",
            "Arguments": "`remove`:  optional field where you can specify if you want to remove the welcome channel",
            "Usage": f"`{p}welcome`: sets the channel\n`{p}welcome remove`: removes the welcome channel"
        },
        "info": {
            "Description": "Shows info about a color",
            "Arguments": "`name/index:  required field where you can specify which color you want to know about",
            "Usage": f"`{p}info red`: shows info if red exists in your set\n`{p}info 2`: shows info about your second color",
        },
        "themes": {
            "Description": "Shows a list of themes to the user",
            "Usage": f"`{p}themes`: will show a picture of the themes",
            "Aliases": f"`{p}t`, `{p}temes`(for carlos)",
        },
        "theme.save": {
            "Description": "Saves the users active colors as a theme",
            "Arguments": "`name`: The name you want the new theme to be called",
            "Usage": f"`{p}theme.save My Theme`: Saves a new theme called 'My Theme'",
            "Aliases": f"`{p}t.s`, `{p}t.save`, `{p}theme.add`",
        },
        "theme.overwrite": {
            "Description": "Overwrites a theme with another one",
            "Arguments": """`name/index`: The name or index of the theme you want to replace
                         `name`: The name of the new theme you are adding""",
            "Usage": f"`{p}theme.overwrite 1 | My new Theme`: Overwrite the first theme with a new theme called 'My new Theme'",
            "Aliases": f"`{p}t.o`, `{p}theme.replace`",
        },
        "theme.remove": {
            "Description": "Deletes a theme",
            "Arguments": "`name/index`: The name or index of the theme you want to remove",
            "Usage": f"`{p}theme.remove 2`: Removes the second theme",
            "Aliases": f"`{p}t.r`, `{p}theme.delete`",
        },
        "theme.load": {
            "Description": "Applies a theme to the server",
            "Arguments": "`name/index`: The name or index of the theme you want to load",
            "Usage": f"`{p}theme.load Vibrant`: Loads a theme called 'Vibrant' if there is one",
            "Aliases": f"`{p}t.l`",
        },
        "theme.info": {
            "Description": "Show a drawn image of your themes",
            "Arguments": "`name/index`: The name or index of the theme you want to see",
            "Usage": f"`{p}theme.info 1`: Shows info about the first theme",
            "Aliases": f"`{p}t.i`",
        },
        "theme.rename": {
            "Description": "Renames a theme",
            "Arguments": """`name/index`: The name or index of the theme you want to rename
                         `name`: The new name of the theme""",
            "Usage": f"`{p}theme.rename 1 | Happy colors`: rename the first theme to 'Happy colors'",
            "Aliases": f"`{p}t.rn`",
        },
    }


change_log = {
    "0.1": {
        "@Vibrant for help": "Users can mention the bot to give info about help",
        "Changeable Prefixes": "Users can change prefix with prefix command to avoid prefix conflict with other bots",
        "Added patch notes": "you can see what I'm doing and I can see what I've done",
        "Color adding prompts removed": "They no longer show up",
        "Changed some help command things": "Made it so they show default prefixes"
    },
    "0.2": {
        "Optimization": "Made many functions like prefix run faster",
        "Optimized Data storage": "improved function input to be more specific to make it faster",
        "Optimized splash command": "Splash runs faster due to better math",
    },
    "0.3": {
        "Overhauled help command": "Gave help a bunch of useful stuff like setup and individual command help",
        "`clear_all_colors` and `set` changed": "Commands now send a backup just incase",
        "Changed data command name": "Changed it to channels since it only shows channel data",
        "Added a force prefix change": "can use vibrantprefix command to avoid overlap"
    },
    "0.4": {
        "Aliased Commands": "Gave a bunch of commands alternate names like add/remove can be create/delete if you want",
        "Removed redundant commands": "removed redundant commands because I figured out how to alias commands",
        "Better Error Handling": "ignores things like command not found and has specific error handling for add command",
    },
    "0.5": {
        "Black color now works": "black no longer shows up as transparent because hex value is auto converted to #000001",
        "Added more presets": "presets work differently and thus there are many more like Bootstrap, Metro, and Icecream",
        "Better Drawing": "Made drawing images for commands like colors look better and more open",
        "Preview command": "new command to show preset colors"
    },
    "0.6": {
        "Changed the look of channels and expose": "Commands are simpler and easier to read",
        "DM Commands": "Some commands like help and howdy work in a DM channel now",
        "Less verbose": "Some commands are less verbose to clear up clutter",
        "More error handling": "Some more errors are handled",
        "Destroyed some bugs": "General stuff like me being stupid"
    },
    "0.7": {
        "The return of reaction based UX": "Reaction based UX is back and works this time",
        "updated pfp algorithm": "Algorithm is more accurate now",
        "DBL integration": "better integration with the API",
        "Hyperlinks": "inline links for help to clean things up"
    },
    "0.8": {
        "Themes(alpha)": "Themes not ready yet but kind of work",
        "Housekeeping": "Cleaned up a bunch of things that weren't necessary",
        "Added some functions to classes": "less imports, better looking",
        "Code documentation": "I can see what everything does easier. so can you if you care",
        "Splash changed": "Splash command now colors in an even distribution of colors",
        "Patchnotes": "Patchnotes doesnt bypass disabled channels now",
        "Help works": "help wont give setup every time",
    },
    "0.9": {
        "Themes": "Themes allow you to save presets which allows switching the feel of the server",
        "Serialization": "Custom serialization per object to allow for the use of sets",
        "The use of python sets": "No more duplicate role members",
        "Clearing colors faster": "Fixed a bug that massively slowed down clearing colors",
        "Smarter updates": "The database is updated less but at better times to save your time",
        "Changed some functions": "Some functions within the code are now faster and smarter",
    },
    "1.0": {
        "Themes Documentation": "Get help with using themes",
        "Segmented help": "More help categories",
        "Importing presets": "Can import named presets as themes",
    },
    "1.1": {
        "Housekeeping": "New techniques for cleaner/faster code",
        "Exceptions": "New way to handle errors should be more descriptive",
        "Less prone to breaking": "Stricter error handling so less confusing errors",
        "Fixed major bug with missing guild problems": "Should handle data better"
    }
}

# wait lists with for reaction based UX
waiting_on_reaction = {}
waiting_on_hexcode = {}

heavy_command_active = {}
