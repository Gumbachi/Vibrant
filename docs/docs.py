"""Holds documentation for the bot in dict form."""


def help_book(p):
    return [
        # Table of Contents
        {
            "title": "Table of Contents",
            "description": f"Navigate between pages with the reaction buttons",
            "1. Vibrant Tutorial": ["Learn how to use the bot and its commands"],
            "2. Theme Tutorial": ["Learn how to use themes"],
            "3. General Commands": ["Shows a list of general commands"],
            "4. Color Commands": ["Shows a list of color related commands"],
            "5. Theme Commands": ["Shows a list of theme related commands"],
            "6. Macros": ["Shows a list of macros the bot has"],
            "7. Alias Dictionary": ["All of the aliases that commands have to make input easier"],
            "-----------------------------": ["[Vote for Vibrant](https://top.gg/bot/589685258841096206/vote) | [Support Server](https://discord.gg/rhvyup5) | [Github](https://github.com/Gumbachi/Vibrant)"]
        },

        # Tutorial
        {
            "title": "Vibrant Tutorial",
            "description": " ",
            "Manage Colors": [
                f"1. Type `{p}add #ff0000 My Color` to add a color",
                f"2. Type `{p}colors` to view your colors",
                f"3. Type `{p}rename 1 | Blue` to rename the color",
                f"4. Type `{p}recolor 1 | #0000ff` to change the look of a color"
            ],
            "Assign Colors": [
                f"1. Type `{p}colorme 1` to color yourself",
                f"2. Type `{p}color @user 1` to color someone else",
                f"3. Type `{p}splash` to color everyone without a color"
            ],
            "Remove Colors": [
                f"1. Type `{p}remove 1` to remove the first color",
                f"2. Type `{p}clear_colors` to remove all colors"
            ],
            "Color New People": [
                f"Welcome people by typing `{p}welcome` in the desired channel. Typing the command again will turn welcoming off",
                "The \"welcome channel\" is where the bot will send Hello/Goodbye messages",
                "With a welcome channel set the bot will randomly color any new member"
            ],
            "Themes": [f"Click the ➡️ to learn about themes"]
        },

        # Theme Tutorial
        {
            "title": "Theme Tutorial",
            "description": "Themes work like save states. They record your colors and the members they are applied to so you can save your setup and use different ones without having to rebuild them",
            "Using Presets": [
                f"1. Type `{p}imports` to see available presets",
                f"2. Type `{p}import vibrant` to import a theme",
                f"3. Type `{p}load vibrant` to set your colors",
                f"4. Type `{p}splash` to apply your colors to the server"
            ],
            "Custom Themes": [
                f"1. Type `{p}save My Theme` to save your current color setup",
                f"2. Type `{p}themes` to view all of your themes",
                f"3. Type `{p}theme.rename My Theme | Custom Theme` to rename a theme"
            ],
            "Manage Themes": [
                f"1. Type `{p}overwrite 1` to replace a theme with your current setup",
                f"2. Type `{p}erase 1` to remove one of your themes"
            ]
        },

        # Commands
        {
            "title": "Commands",
            "description": f"`{p}command <argument>`.\n`*` indicates an optional argument\n`<color>` can be a name or index",
            "General Commands": [
                f"`{p}prefix <new prefix*>` -- Changes the prefix the bot uses",
                f"`{p}welcome` -- Toggles a channel for greeting users"
            ],
            "Color Management Commands": [
                f"`{p}colors` -- Shows available colors",
                f"`{p}add <hexcode> <name*>` -- Adds a color",
                f"`{p}remove <color>` -- Removes a color",
                f"`{p}rename <color>|<name>` -- Changes a color's name",
                f"`{p}recolor <color>|<hexcode>` -- Changes a color's looks",
                f"`{p}clear_colors` -- Clears all of the colors"
            ],
            "Color Assignment Commands": [
                f"`{p}colorme <color*>` -- Assigns you your desired color or random",
                f"`{p}color <user> <color*>` -- Gives a specific user a color",
                f"`{p}uncolorme` -- Removes your color if you have one",
                f"`{p}splash <color*>` -- Gives a color to everyone in the server without one",
                f"`{p}unsplash` -- Uncolors everyone"
            ]
        },

        # Theme Commands
        {
            "title": "Theme Commands",
            "description": f"{p}command <argument>.\n`*` indicates an optional argument\n`<theme>` can be a name or index",
            "Theme Commands": [
                f"`{p}themes` -- Draws a pretty list of themes",
                f"`{p}imports` - - Shows available presets"
            ],
            "Theme Management Commands": [
                f"`{p}save <name*>` -- Saves your theme",
                f"`{p}theme.remove <theme>` -- Deletes a theme",
                f"`{p}overwrite <theme>` -- Replaces a theme",
                f"`{p}load <theme>` -- Applies a saved theme to your server",
                f"`{p}theme.rename <theme>|<name>` -- Changes a theme's name",
                f"`{p}import <name>` -- Adds a preset as a theme"
            ]
        },

        # Macros
        {
            "title": "Macros",
            "description": f"Macros are a way to execute multiple commands with one single command.\nThey make things clean and convenient",
            "Import, Load, Splash, Overwrite": [
                f"`{p}ilso <name>` -- Imports a preset, Loads that preset, Splashes everyone with a random color, Overwrites the imported theme with member colors"
            ],
            "Add, Colorme": [f"`{p}acm` -- Adds a color and then applies it to you"],
            "Suggestions": ["If you have suggestions for macros you would like then please let me know in the support server"]
        },

        # Alias Dictionary
        {
            "title": "Command Aliases",
            "description": "Most commands have shorthand aliases\nAny commands with `color` in the name have an alias with `colour`",
            "Color Commands": [
                f"`{p}colors` -- `{p}c`",
                f"`{p}color` -- `{p}cu`",
                f"`{p}colorme` -- `{p}me`, `{p}cm`",
                f"`{p}uncolorme` -- `{p}ucm`",
                f"`{p}add` -- `{p}new`",
                f"`{p}remove` -- `{p}delete`",
                f"`{p}rename` -- `{p}rn`",
                f"`{p}recolor` -- `{p}rc`"
            ],
            "Theme Commands": [
                f"`{p}themes` -- `{p}t`, `{p}temes`",
                f"`{p}imports` -- `{p}presets`",
                f"`{p}load` -- `{p}theme.load`",
                f"`{p}save` -- `{p}saveas`, `{p}theme.save`",
                f"`{p}theme.remove` -- `{p}t.r`, `{p}t.d`",
                f"`{p}overwrite` -- `{p}theme.overwrite`",
                f"`{p}theme.rename` - - `{p}t.rn`"
            ],
            "Other Commands": [
                f"`{p}prefix` -- `{p}vibrantprefix`"
            ]
        }
    ]


change_log = {
    "0.1": {
        "title": "Vibrant 0.1",
        "description": " ",
        "@Vibrant for help": "Users can mention the bot to give info about help",
        "Changeable Prefixes": "Users can change prefix with prefix command to avoid prefix conflict with other bots",
        "Added patch notes": "you can see what I'm doing and I can see what I've done",
        "Color adding prompts removed": "They no longer show up",
        "Changed some help command things": "Made it so they show default prefixes"
    },
    "0.2": {
        "title": "Vibrant 0.2",
        "description": " ",
        "Optimization": "Made many functions like prefix run faster",
        "Optimized Data storage": "improved function input to be more specific to make it faster",
        "Optimized splash command": "Splash runs faster due to better math",
    },
    "0.3": {
        "title": "Vibrant 0.3",
        "description": " ",
        "Overhauled help command": "Gave help a bunch of useful stuff like setup and individual command help",
        "`clear_all_colors` and `set` changed": "Commands now send a backup just incase",
        "Changed data command name": "Changed it to channels since it only shows channel data",
        "Added a force prefix change": "can use vibrantprefix command to avoid overlap"
    },
    "0.4": {
        "title": "Vibrant 0.4",
        "description": " ",
        "Aliased Commands": "Gave a bunch of commands alternate names like add/remove can be create/delete if you want",
        "Removed redundant commands": "removed redundant commands because I figured out how to alias commands",
        "Better Error Handling": "ignores things like command not found and has specific error handling for add command",
    },
    "0.5": {
        "title": "Vibrant 0.5",
        "description": " ",
        "Black color now works": "black no longer shows up as transparent because hex value is auto converted to #000001",
        "Added more presets": "presets work differently and thus there are many more like Bootstrap, Metro, and Icecream",
        "Better Drawing": "Made drawing images for commands like colors look better and more open",
        "Preview command": "new command to show preset colors"
    },
    "0.6": {
        "title": "Vibrant 0.6",
        "description": " ",
        "Changed the look of channels and expose": "Commands are simpler and easier to read",
        "DM Commands": "Some commands like help and howdy work in a DM channel now",
        "Less verbose": "Some commands are less verbose to clear up clutter",
        "More error handling": "Some more errors are handled",
        "Destroyed some bugs": "General stuff like me being stupid"
    },
    "0.7": {
        "title": "Vibrant 0.7",
        "description": " ",
        "The return of reaction based UX": "Reaction based UX is back and works this time",
        "updated pfp algorithm": "Algorithm is more accurate now",
        "DBL integration": "better integration with the API",
        "Hyperlinks": "inline links for help to clean things up"
    },
    "0.8": {
        "title": "Vibrant 0.8",
        "description": " ",
        "Themes(alpha)": "Themes not ready yet but kind of work",
        "Housekeeping": "Cleaned up a bunch of things that weren't necessary",
        "Added some functions to classes": "less imports, better looking",
        "Code documentation": "I can see what everything does easier. so can you if you care",
        "Splash changed": "Splash command now colors in an even distribution of colors",
        "Patchnotes": "Patchnotes doesnt bypass disabled channels now",
        "Help works": "help wont give setup every time",
    },
    "0.9": {
        "title": "Vibrant 0.9",
        "description": " ",
        "Themes": "Themes allow you to save presets which allows switching the feel of the server",
        "Serialization": "Custom serialization per object to allow for the use of sets",
        "The use of python sets": "No more duplicate role members",
        "Clearing colors faster": "Fixed a bug that massively slowed down clearing colors",
        "Smarter updates": "The database is updated less but at better times to save your time",
        "Changed some functions": "Some functions within the code are now faster and smarter",
    },
    "1.0": {
        "title": "Vibrant 1.0",
        "description": " ",
        "Themes Documentation": "Get help with using themes",
        "Segmented help": "More help categories",
        "Importing presets": "Can import named presets as themes",
    },
    "1.1": {
        "title": "Vibrant 1.1",
        "description": " ",
        "Housekeeping": "New techniques for cleaner/faster code",
        "Exceptions": "New way to handle errors should be more descriptive",
        "Less prone to breaking": "Stricter error handling so less confusing errors",
        "Fixed major bug with missing guild problems": "Should handle data better"
    },
    "1.2": {
        "title": "Vibrant 1.2",
        "description": " ",
        "Overlapping data": "Member data should be handled properly due to a fixed constructor error",
        "Unsplash is faster": "unsplash just deletes roles which should make it faster",
        "Help update": "Help command is simplified and now works like a book with buttons",
        "Overwrite simpler": "Overwrite just overwrite a theme now without changing name",
        "imports command": "You can now view all presets",
        "Pages for everything": "Everything that can be paginated is",
        "Better UX": "Asks for hexcode and then colors the user you wanted"
    },
    "1.3": {
        "title": "Vibrant 1.3",
        "description": " ",
        "Smarter data handling": "Tries to fill in gaps with the data before reporting error",
        "Paginated Images changed": "No more double images its just one now for simplicity",
        "Back to PNG": "Apparently WebP doesn't work on iOS :(",
        "Visual Changes": "Switched a lot of responses to embeds"
    },
    "1.4": {
        "title": "Vibrant 1.4",
        "description": " ",
        "Role positioning": "Creates roles under the bot role instead of at the bottom",
        "Theme limit": "Changed default limit to 5"
    },
    "2.0": {
        "title": "Vibrant 2.0(rewrite)",
        "description": "Same bot but written better",
        "No more channel disabling": "got rid of a useless feature",
        "Better databasing": "better database interaction",
        "less code": "less code = better",
        "less data": "bot stores less data",
    },
    "2.1": {
        "title": "Vibrant 2.1",
        "description": "Added Macros",
        "Macros": "Run multiple commands in common patterns with one command",
        "Caught some errors": "Caught 50001 and 50013 API Errors"
    }
}
