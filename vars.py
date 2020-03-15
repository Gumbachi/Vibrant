import discord
from discord.ext import commands
from cfg import coll

# Cogs the bot loads
extensions = [
    "cogs.basic",
    "cogs.channels",
    "cogs.color.color_assignment",
    "cogs.color.color_info",
    "cogs.color.color_management",
    "cogs.errors",
    # 'cogs.themes',
    # 'cogs.utility',
    # 'cogs.dbl'
]

emoji_dict = {"checkmark": "✅",
              "crossmark": "❌"}

preset_names = [
    "basic",
    "vibrant",
    "rainbow",
    "metro",
    "bootstrap",
    "icecream",
    "neon",
    "pastel",
    "outrun",
    "sunset",
    "downtown",
    "discord",
    "christmas",
    "bridge",
    "redtoblack"
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
        data = coll.find_one({"id": id})
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
    help_dict = {
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
                                    `{p}expose <name>`: Shows some info about a member
                                    `{p}pfp <user>`: sends a hexcode that matches the user's pfp
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
    return help_dict


def get_commands(p):
    command_dict = {
        "help": {
            "Description": "Do you really need one?",
            "Usage": f"`{p}help`: You know what this does",
            "Aliases": "info",
        },
        "howdy": {
            "Description": "A friendly function that replies howdy",
            "Usage": f"`{p}howdy`",
            "More Information": """Will reply howdy in the channel the command was sent in unless the channel is disabled which it will then message the user"""
        },
        "expose": {
            "Description": "Shows information about a user like favorite color, roles, join date, etc.",
            "Fields": "user: this is an optional field where you can @mention a user or type in their name to find a user",
            "Usage": f"`{p}expose`: Will display expose message for you\n`{p}expose @Gumbachi`: Will find gumbachi\n`{p}expose Gumbachi`: Will try to find a user named similarly to Gumbachi",
            "Aliases": "whois",
            "More Information": f"""-Leaving the user field blank will apply the command to yourself
                                    -The command will try to use fuzzy matching to find a user closest to your search such as `{p}expose gum` will result in it searching for a user with a name similar to 'gum'"""
        },
        "pfp": {
            "Description": "A command that analyzes a profile picture(pfp) and tries to find the most vibrant color",
            "Fields": "user: this is an optional field where you can @mention to find someone",
            "Usage": f"`{p}pfp`: Applies to you\n`{p}pfp @Gumbachi`: applies to mentioned user",
            "More Information": """If the user field is left blank then the command applies to yourself"""
        },
        "colorme": {
            "Description": "Will give you a color",
            "Fields": "name/index: this is an optional field where you can input a specific color index or name to get a specific color",
            "Usage": f"`{p}colorme`: Colors you a random color\n`{p}colorme blue`: Colors you blue if the color exists\n`{p}colorme 2`: Colors you whatever color is in the 2nd slot of the set",
            "Aliases": "colourme\nme",
            "More Information": """-Will give you a random color if name/index is left blank
                                   -I would recommend using index to avoid mixup. Fuzzy matching isnt perfect"""
        },
        "color": {
            "Description": "Colors another user",
            "Fields": "user: this is a required field where you can @mention a user or type in their name to find a user\ncolor/index: this is an optional field where you can input a specific color index or name to get a specific color",
            "Usage": f"`{p}color @gumbachi`: Colors the mentioned user a random color\n`{p}color @gumbachi 2`: colors the mentioned user the 2nd color\n`{p}color Gumbachi blue`",
            "Aliases": "colour",
            "More Information": """-Will give random color if color/index field is left blank
                                   -Uses fuzzy matching to try to match misspelled names for convenience"""
        },
        "colors": {
            "Description": "Generates an image of all the colors and sends it",
            "Usage": f"`{p}colors`",
            "Aliases": "colours\ncolorset\ncolourset",
            "More Information": """-If channel is disabled then it will DM you the message
                                   -Uses python Pillow library to draw a custom image to send"""
        },
        "splash": {
            "Description": "Colors everyone without a color in the server",
            "Usage": f"`{p}splash`",
            "Aliases": "colorall\ncolourall",
            "More Information": """-This commands takes time because of API abuse. Everytime a person gets colored, a role may be created and a role is assigned which require
                                   API calls and spamming it is considered abuse. To avoid this the bot will color 5 people, wait 5 seconds and then repeat until done
                                   -The bot sends an estimated time message for how long the commands will take"""
        },
        "add": {
            "Description": "Adds a custom color to the colorset",
            "Fields": """hexcode: this is a required field where you can input a hexcode for your desired color
                         name: this is an optional field for the name of your new color""",
            "Usage": f"`{p}add #ff0000 Red`: Adds a color named red to the set\n`{p}add #ffff00`:Adds a color named 'Color x' to the set",
            "Aliases": "new\ncreate",
            "More Information": """-Will give the color a name like 'Color 2' if name field left blank"""
        },
        "enable": {
            "Description": "Enables the channel it is typed in",
            "Fields": """all: this is an optional field where you can type all to specify if you want all channels enabled""",
            "Usage": f"`{p}enable`: enable just this channel\n`{p}enable all`: enable all channels"
        },
        "remove": {
            "Description": "Removes a color from the colorset",
            "Fields": """color/index: this is a required field where you can input a color name or index for your desired color""",
            "Usage": f"`{p}remove Red`: Will try to remove a color named red\n`{p}remove 3`: Removes the color in the 3rd slot",
            "Aliases": "delete",
        },
        "rename": {
            "Description": "Renames a color in the colorset",
            "Fields": """color/index: this is a required field where you can type a color name or index to change
                         new name: this is a required field for the new name of the color""",
            "Usage": f"`{p}rename blue | red`: Will rename a color named blue to red\n`{p}rename 4 | Blue`: Renames the 4th color to Blue",
            "More Information": """Uses a `|` separator to split the before and after"""
        },
        "recolor": {
            "Description": "Changes a color's look",
            "Fields": """color/index: this is a required field where you can type a color name or index to change
                         new hexcode: this is a required field for the new hexcode of the color""",
            "Usage": f"`{p}recolor blue | #0000ff`: Will change the value of blue to #0000ff(blue)\n`{p}recolor 4 | #ffffff`: Changes the value of the 4th color to #ffffff(white)",
            "Aliases": "recolour",
            "More Information": """Uses a `|` separator to split the before and after"""
        },
        "prefix": {
            "Description": "Changes the server prefix",
            "Fields": """new prefix: this is a required field for the new prefix""",
            "Usage": f"`{p}prefix $`: Will change prefix to $\n`{p}vibrantprefix $`: Does the same thing under a different alias",
            "Aliases": "vibrantprefix",
            "More Information": f"""if you have overlap issues then use `{p}vibrantprefix new_prefix` to dodge bot overlap"""
        },
        "clear_all_colors": {
            "Description": "Will remove all colors from a colorset",
            "Usage": f"`{p}clear_all_colors`",
            "Aliases": "clear_all_colours",
            "More Information": """-Is made difficult on purpose to avoid accidents
                                   -Will send a backup incase you made a mistake:)"""
        },
        "channels": {
            "Description": "Sends channel information",
            "Usage": f"`{p}channels`",
            "Aliases": "data",
            "More Information": """If channel is disabled then it will DM you the message"""
        },
        "export": {
            "Description": "Creates a JSON file cotaining your colorset",
            "Usage": f"`{p}export`"
        },
        "version": {
            "Description": "Sends a message containing patch notes",
            "Fields": """version: this is an optional for the version you want to see""",
            "Usage": f"`{p}version`: Sends latest\n`{p}version 1.4`: sends v1.4 notes",
            "Aliases": "patchnotes",
        },
        "import": {
            "Description": "Imports a theme from from a preset",
            "Fields": "name: The name of the preset you want to import",
            "Usage": f"`{p}import vibrant`: Imports the vibrant preset as a theme",
        },
        "disable": {
            "Description": "Disables the channel it is typed in",
            "Fields": """all: this is an optional field where you can type all to specify if you want all channels disabled""",
            "Usage": f"`{p}disable`: disable just this channel\n`{p}disable all`: disable all channels"
        },
        "report": {
            "Description": "Sends a message to me(Gumbachi). you can just say 'Hi' if you want to:).",
            "Fields": "message: this is a required containing your message",
            "Usage": f"`{p}report Hi Gum`: Sends 'Hi Gum' to me",
            "More Information": """Support Server if its urgent: https://discord.gg/rhvyup5"""
        },
        "status": {
            "Description": "Sends a message saying if the channel is enable or not",
            "Usage": f"`{p}status`"
        },
        "welcome": {
            "Description": "Sets or removed the welcome channel",
            "Fields": """remove: this is an optional field where you can specify if you want to remove the welcome channel""",
            "Usage": f"`{p}welcome`: sets the channel\n`{p}welcome remove`: removes the welcome channel"
        },
        "info": {
            "Description": "Shows info about a color",
            "Fields": """name/index: this is an required field where you can specify which color you want to know about""",
            "Usage": f"`{p}info red`: shows info if red exists in your set\n`{p}info 2`: shows info about your second color",
            "Aliases": "about",
        },
        "themes": {
            "Description": "Shows a list of themes to the user",
            "Usage": f"`{p}themes`: will show a picture of the themes",
            "Aliases": f"`{p}t`, `{p}temes`(for carlos)",
        },
        "theme.save": {
            "Description": "Saves the users active colors as a theme",
            "Fields": "name: The name you want the new theme to be called",
            "Usage": f"`{p}theme.save My Theme`: Saves a new theme called 'My Theme'",
            "Aliases": f"`{p}t.s`, `{p}t.save`, `{p}theme.add`, `{p}t.add`",
        },
        "theme.overwrite": {
            "Description": "Overwrites a theme with another one",
            "Fields": """name/index: The name or index of the theme you want to replace
                         name: The name of the new theme you are adding""",
            "Usage": f"`{p}theme.overwrite 1 | My new Theme`: Overwrite the first theme with a new theme called 'My new Theme'",
            "Aliases": f"`{p}t.o`, `{p}t.replace`, `{p}t.overwrite`",
        },
        "theme.remove": {
            "Description": "Deletes a theme",
            "Fields": """name/index: The name or index of the theme you want to remove""",
            "Usage": f"`{p}theme.remove 2`: Removes the second theme",
            "Aliases": f"`{p}t.remove`, `{p}t.r`, `{p}theme.delete`, `{p}t.delete`, `{p}t.d`",
        },
        "theme.load": {
            "Description": "Applies a theme to the server",
            "Fields": """name/index: The name or index of the theme you want to load""",
            "Usage": f"`{p}theme.load Vibrant`: Loads a theme called 'Vibrant' if there is one",
            "Aliases": f"`{p}t.load`, `{p}t.l`",
        },
        "theme.info": {
            "Description": "Shows info about a given theme",
            "Fields": """name/index: The name or index of the theme you want to see""",
            "Usage": f"`{p}theme.info 1`: Shows info about the first theme",
            "Aliases": f"`{p}t.i`, `{p}t.info`",
        },
        "theme.rename": {
            "Description": "Renames a theme",
            "Fields": """name/index: The name or index of the theme you want to rename
                         name: The new name of the theme""",
            "Usage": f"`{p}theme.rename 1 | Happy colors`: rename the first theme to 'Happy colors'",
            "Aliases": f"`{p}t.rename`, `{p}t.rn`",
        },






    }
    return command_dict


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
        "Exceptions": "New way to handle errors should be more descriptive"
    }
}

# wait lists with for reaction based UX
waiting_on_reaction = {}
waiting_on_hexcode = {}
waiting_on_pfp = {}

heavy_command_active = {}

statbuffer = {
    "howdies": 0,
    "users_colored": 0,
    "colors_created": 0,
    "colors_removed": 0,
    "total_colors": 0,
    "total_users": 0,
    "servers": 0
}
