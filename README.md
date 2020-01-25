# ColorBOT

A discord bot that can make a server fun and colorful.
This bot manages colorful roles for a discord server ie. creation, deletion, editing of roles in a server.
You can view how to setup and use commands with the bot using the help command after inviting the bot to your server/guild
If you forgot your prefix then you can @mention the bot for help

## What makes this bot special

1. This bot is special because it can do things like save and use different themes, disable channels, and has helpful commands like splash which can color everybody so you don't have to do it all yourself.
2. The syntax for commands is intuitive for commands like colorme, add, remove which are also aliased for ease of use (e.g. colourme works too for those with the extra 'u')
3. The bot also manages your roles so if you aren't using a color then it is removed until you use it again. This cuts down on role clutter

## Features

* Create and manage custom color roles
* Color people and yourself with commands
* Customizable prefix
* Randomly color everyone or specific people
* Welcome new members and assign them colors
* Get a color to match your profile picture
* Save themes/presets for when you feel like change but dont want to lose your current setup
* Auto role management keeps the server clean and also updates info if somebody changes a role to keep your colors and discord connected perfectly

## Setup

**1.** Invite the [bot](https://discordapp.com/api/oauth2/authorize?client_id=589685258841096206&permissions=268561488&redirect_uri=https%3A%2F%2Fdiscordapp.com%2Foauth2%2Fauthorize%3F%26client_id%3D589685258841096206%26scope%3Dbot&scope=bot) to your server
**2.** Type `$help 1` in a text channel to view setup instructions and to get a basic understanding of how to use the bot. Note that '$' is the default prefix and may change if you decide to, in which case you need to use your custom prefix
**3.** Follow the setup through until the end and you should have a basic understanding of how to use the bot>

## General Commands

|      **Command**     |      **Example**     |                               **Description**                              |
|:--------------------:|:--------------------:|:--------------------------------------------------------------------------:|
| help \<page>         | $help setup          | Standard help command. You know what it does                               |
| prefix \<new prefix> | $prefix %            | Changes the prefix you use to call commands                                |
| expose \<user>       | $expose @Gumbachi    | Shows general information about a person in the server                     |
| pfp \<user>          | $pfp @Gumbachi       | Tries its hardest to find the prominent color of the users profile picture |
| report \<msg>        | $report Bot's busted | Sends me a direct message. Should be used to report bugs                   |

## Main Color Commands

|             **Command**             |       **Example**       |                                 **Description**                                |
|:-----------------------------------:|:-----------------------:|:------------------------------------------------------------------------------:|
| colorme \<color/index>              | $colorme 3              | Colors the user their desired color. Colors user randomly if not given a color |
| color \<user> \<color/index>        | $color @Gumbachi Blue   | Colors a specific user a specific color                                        |
| colors                              | $colors                 | Shows a nicely laid out grid of your colors                                    |
| add \<hexcode> \<name>              | $add #FFC0CB Pink       | Adds a color to your active colors                                             |
| remove \<name/index>                | $remove pink            | Removes a color from your active colors                                        |
| rename \<name/index> \| \<new name> | $rename pink | blue     | Renames a color in your active colors                                          |
| recolor \<name\index> \| \<hexcode> | $recolor pink | #0000FF | Changes a color's hex code which changes the way it looks                      |

## Other Color Commands

|   **Command**   |    **Example**   |                                                **Description**                                                |
|:---------------:|:----------------:|:-------------------------------------------------------------------------------------------------------------:|
| splash \<color> | $splash          | Will color everyone in the server who isn't already colored. Providing a color will color everyone that color |
| set \<preset>   | $set vibrant     | Changes the active colors to a preset set of colors                                                           |
| presets         | $presets         | Shows a list of presets to choose from                                                                        |
| preview         | $preview vibrant | Shows a preview of the preset                                                                                 |
| info \<color>   | $info Red        | Shows info about a color like members it belongs to and hexcode                                               |
| export          | $export          | Provides a JSON file with a backup of your color loadout                                                      |
| import          | $import          | When sent with a valid JSON attachment it will set the JSON file's colors as your active colors               |

## Channel Commands

|    **Command**    | **Example** |                                                   **Description**                                                   |
|:-----------------:|:-----------:|:-------------------------------------------------------------------------------------------------------------------:|
| enable \<all>     | $enable     | Will enable a channel if disabled. 'all' is an optional argument to enable all channels                             |
| disable \<all>    | $disable    | Will disable a channel if enabled. 'all' is an optional argument to disable all channels                            |
| welcome \<remove> | $welcome    | Sets the welcome channel of the server where greetings will be sent and colors will be auto-assigned to new members |
| status            | $status     | Provides the status of the channel                                                                                  |
| channels          | $channels   | Provides a list of all enabled and disabled channels. Also shows the welcome channel                                |

## About the Bot

This bot is written in python using the discord.py library and makes use of other libraries like pillow to draw images to make viewing colors easy
The bot stores information about your colors in a MongoDB database so if the bot goes offline you don't lose your data

## Support Server

If you couldn't find what you were looking for with the help command, have any general questions you need answered, or just want to see the bot in action before you invite it then join the [Support Server](https://discord.gg/rhvyup5)

<a href="https://top.gg/bot/589685258841096206" >
  <img src="https://top.gg/api/widget/589685258841096206.svg" alt="ColorBOT" />
</a>
