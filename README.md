# Vibrant

A discord bot that can make a server fun and colorful.  
This bot manages colorful roles for a discord server ie. creation, deletion, editing of roles in a server.  
You can view how to setup and use commands with the bot using the help command after inviting the bot to your server.  
If you forgot your prefix then you can @mention the bot for help.

## What makes this bot special

1. This bot is special because it can do things like save and use different themes, disable channels, and has helpful commands like splash which can color everybody so you don't have to do it all yourself.
2. The syntax for commands is intuitive for commands like colorme, add, remove which are also aliased for ease of use (e.g. colourme works too for those with the extra 'u')
3. The bot also manages your roles so if you aren't using a color then it is removed until you use it again. This cuts down on role clutter

## More Features

- Create and manage custom color roles
- Color people and yourself with commands
- Customizable prefix
- Randomly color everyone or specific people
- Welcome new members and assign them colors
- Save themes/presets for when you feel like change but dont want to lose your current setup
- Auto role management keeps the server clean and also updates info if somebody changes a role to keep your colors and discord connected perfectly

## Setup

1. Invite the [bot](https://discordapp.com/api/oauth2/authorize?client_id=589685258841096206&permissions=268545088&redirect_uri=https%3A%2F%2Fdiscordapp.com%2Foauth2%2Fauthorize%3F%26client_id%3D589685258841096206%26scope%3Dbot&scope=bot) to your server
2. Type `$help 1` in a text channel to view setup instructions and to get a basic understanding of how to use the bot. Note that '\$' is the default prefix and may change if you decide to, in which case you need to use your custom prefix
3. Follow the setup through until the end and you should have a basic understanding of how to use the bot

## Commands

Optional arguments are marked with a \*

### General Commands

|      **Command**       | **Example**  |               **Description**               |
| :--------------------: | :----------: | :-----------------------------------------: |
|     help \<page\*>     | \$help setup |            Standard help command            |
| prefix \<new prefix\*> |  \$prefix %  | Changes the prefix you use to call commands |

### Color General Commands

|  **Command**   |      **Example**      |           **Description**            |
| :------------: | :-------------------: | :----------------------------------: |
|     colors     |       \$colors        | Shows an image of your active colors |
| info \<color>  |      \$info Red       |  Shows info about a specific color   |
| convert \<rgb> | \$convert 123,123,123 |        Convert RGB to hexcode        |

### Color Management Commands

|          **Command**           |      **Example**       |             **Description**             |
| :----------------------------: | :--------------------: | :-------------------------------------: |
|    add \<hexcode> \<name\*>    |   \$add #FFC0CB Pink   |   Adds a color to your active colors    |
|        remove \<color>         |     \$remove pink      | Removes a color from your active colors |
|   rename \<color> \| \<name>   | \$rename pink \| blue  |  Renames a color in your active colors  |
| recolor \<color> \| \<hexcode> | \$recolor 2 \| #0000FF |     Changes the way the color looks     |
|        clear_all_colors        |   \$clear_all_colors   |        Removes all active colors        |

### Color Assignment Commands

|          **Command**           |     **Example**     |      **Description**      |
| :----------------------------: | :-----------------: | :-----------------------: |
|    colorme \<color/index\*>    |     \$colorme 3     |     Colors the sender     |
| color \<user> \<color/index\*> | \$color @Gumbachi 2 |  Colors a specific user   |
|       splash \<color\*>        |      \$splash       | Colors everyone who isn't |
|      unsplash \<color\*>       |     \$unsplash      |     Uncolors everyone     |

### Theme General Commands

|  **Command**  |  **Example**   |           **Description**           |
| :-----------: | :------------: | :---------------------------------: |
|    themes     |    \$themes    | Shows an image of your added themes |
| info \<theme> | \$info vibrant |  Shows info about a specific theme  |
|    imports    |   \$imports    |       Shows a list of presets       |

### Theme Management Commands

|              **Command**               |       **Example**        |           **Description**           |
| :------------------------------------: | :----------------------: | :---------------------------------: |
|            import \<preset>            |     \$import Outrun      | Adds a preset theme to saved themes |
|          theme.save \<name\*>          |      \$t.s My Theme      |   Saves current colors as a theme   |
|        theme.load \<name/index>        |      \$t.l vibrant       |     Loads a saved theme for use     |
|       theme.remove \<name/index>       |      \$t.r vibrant       |           Removes a theme           |
|        theme.overwrite \<name>         |      \$t.o vibrant       |      overwrites a saved theme       |
| theme.rename \<color/index> \| \<name> | \$t.rn vibant \| Vibrant |        Renames a saved theme        |

### Channel Commands

|     **Command**     | **Example** |                   **Description**                    |
| :-----------------: | :---------: | :--------------------------------------------------: |
|   enable \<all\*>   |  \$enable   |             Enable a channel if disabled             |
|  disable \<all\*>   |  \$disable  |             Disable a channel if enabled             |
| welcome \<remove\*> |  \$welcome  |               Sets the welcome channel               |
|       status        |  \$status   |          Provides the status of the channel          |
|      channels       | \$channels  | Provides a list of all enabled and disabled channels |

## Support Server

If you couldn't find what you were looking for with the help command, have any general questions you need answered, or just want to see the bot in action before you invite it then join the [Support Server](https://discord.gg/rhvyup5)

<a href="https://top.gg/bot/589685258841096206" >
  <img src="https://top.gg/api/widget/589685258841096206.svg" alt="Vibrant" />
</a>
