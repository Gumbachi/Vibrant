# Vibrant

A discord bot that can apply themes to spice up your server.  
This bot manages roles for a discord server ie. creation, deletion, editing of roles in a server.  
You can view how to setup and use commands with the bot using the help command after inviting the bot to your server.  
If you forgot your prefix then you can type @Vibrant for help.

## Features

- Create and manage custom color roles
- Color people and yourself with commands
- Save themes/presets for when you feel like change but dont want to lose your current setup
- Auto role management keeps the server clean and also updates info if somebody changes a role to keep your colors and discord connected perfectly
- Customizable prefix
- Randomly color everyone or specific people
- Welcome new members and assign them colors

## Setup

1. Invite the [bot](tinyurl.com/xynj73n5) to your server
2. Type `$help` in a text channel to view setup instructions and to get a basic understanding of how to use the bot. Note that '\$' is the default prefix and may change if you decide to, in which case you need to use your custom prefix
3. Navigate through the help pages until the end and you should have a basic understanding of how to use the bot

## Commands

Optional fields are marked with a \*
\<color> and \<theme> arguments can be either a name or an index

### General Commands

|      **Command**       | **Example** |             **Description**              |
| :--------------------: | :---------: | :--------------------------------------: |
|          help          |   \$help    |          Standard help command           |
| prefix \<new prefix\*> | \$prefix %  | Changes the prefix used to call commands |
|        welcome         |  \$welcome  |      Toggles the welcoming channel       |

### Color Management Commands

|          **Command**           |      **Example**       |             **Description**             |
| :----------------------------: | :--------------------: | :-------------------------------------: |
|    add \<hexcode> \<name\*>    |   \$add #FFC0CB Pink   |   Adds a color to your active colors    |
|        remove \<color>         |     \$remove pink      | Removes a color from your active colors |
|   rename \<color> \| \<name>   | \$rename pink \| blue  |  Renames a color in your active colors  |
| recolor \<color> \| \<hexcode> | \$recolor 2 \| #0000FF |     Changes the way the color looks     |
|          clear_colors          |     \$clear_colors     |        Removes all active colors        |

### Color Assignment Commands

|       **Command**        |     **Example**     |          **Description**          |
| :----------------------: | :-----------------: | :-------------------------------: |
|    colorme \<color\*>    |     \$colorme 3     |            Colors you             |
|        uncolorme         |     \$uncolorme     |           Uncolors you            |
| color \<user> \<color\*> | \$color @Gumbachi 2 |      Colors a specific user       |
|    splash \<color\*>     |      \$splash       | Colors everyone who isn't colored |
|         unsplash         |     \$unsplash      |         Uncolors everyone         |

### Theme General Commands

| **Command** | **Example** |           **Description**           |
| :---------: | :---------: | :---------------------------------: |
|   themes    |  \$themes   | Shows an image of your added themes |
|   imports   |  \$imports  |       Shows a list of presets       |

### Theme Management Commands

|           **Command**            |       **Example**        |           **Description**           |
| :------------------------------: | :----------------------: | :---------------------------------: |
|         import \<preset>         |     \$import Outrun      | Adds a preset theme to saved themes |
|          save \<name\*>          |     \$save My Theme      |   Saves current colors as a theme   |
|          load \<theme>           |      \$load vibrant      |     Loads a saved theme for use     |
|      theme.remove \<theme>       |      \$t.r vibrant       |           Removes a theme           |
|        overwrite \<name>         |   \$overwrite vibrant    |      overwrites a saved theme       |
| theme.rename \<theme> \| \<name> | \$t.rn vibant \| Vibrant |        Renames a saved theme        |

## Support Server

If you couldn't find what you were looking for with the help command, have any general questions you need answered, or just want to see the bot in action before you invite it then join the [Support Server](https://discord.gg/rhvyup5)

<a href="https://top.gg/bot/589685258841096206" >
  <img src="https://top.gg/api/widget/589685258841096206.svg" alt="Vibrant" />
</a>
