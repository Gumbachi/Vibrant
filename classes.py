import copy
import io
import json
import math
import os
import random

import discord
from fuzzywuzzy import process
from PIL import Image, ImageDraw, ImageFont

from vars import bot
from functions import hex_to_rgb


class Guild():
    """Guild object that stores preferences for a guild the bot is in

    Args:
        name (str): The name of the guild
        id (int): The id of the guild from discord
        prefix (str): The custom guild command prefix
        welcome_channel (int): The id of the greeting channel
        disabled_channels (list of int): list of ids of disabled channels
        theme_limit (int): The maximum amount of themes a guild can have
        color_limit (int): The maximum number of colors a guild can have

    Attributes:
        name (str): The name of the guild
        id (int): The id of the guild from discord
        prefix (str): The custom guild command prefix
        welcome_channel (int): The id of the greeting channel
        disabled_channels (list of int): list of ids of disabled channels
        colors (list of Color): list of Color objects the guild has
        themes (list of Theme): list of Theme objects the guild has
        theme_limit (int): The maximum amount of themes a guild can have
        color_limit (int): The maximum number of colors a guild can have
    """
    _guilds = {}  # dict of guilds that have been created

    def __init__(self, id, prefix='$', welcome_channel_id=None,
                 disabled_channel_ids=set(), theme_limit=3, color_limit=25,
                 themes=[], colors=[]):
        self.name = str(bot.get_guild(id))
        self.id = id
        self.prefix = prefix
        self.welcome_channel_id = welcome_channel_id
        self.disabled_channel_ids = disabled_channel_ids
        self.theme_limit = theme_limit
        self.color_limit = color_limit
        self.themes = themes
        self.colors = colors

        Guild._guilds[id] = self  # add guild to the dict

    @property
    def enabled_channels(self):
        """Returns a list of enabled discord channels"""
        return [channel for channel in bot.get_guild(self.id).text_channels
                if channel.id not in self.disabled_channel_ids]

    @property
    def disabled_channels(self):
        """Returns a list of disabled discord channels"""
        return [channel for channel in self.discord_guild.text_channels
                if channel.id in self.disabled_channel_ids]

    @property
    def welcome_channel(self):
        """Returns the welcome channel if it exists"""
        return bot.get_channel(self.welcome_channel_id)

    @property
    def discord_guild(self):
        return bot.get_guild(self.id)

    @property
    def members(self):
        return self.discord_guild.members

    def __repr__(self):
        """
        Output a string that represents the guild object and
        cleanly displays data
        """
        out = (f"Name: {self.name}\nID: {self.id}\nPrefix: {self.prefix}\n"
               f"Welcome: {str(self.welcome_channel)}\n"
               f"Theme Limit: {self.theme_limit}\n"
               f"Color Limit: {self.color_limit}\n")

        out += "Colors\n"
        for color in self.colors:
            out += f"    {repr(color)}\n"

        return out

    def __str__(self):
        return self.name

    def get_role(self, id):
        """Get a discord role from a given ID."""
        discord_guild = self.discord_guild
        if discord_guild:
            return discord_guild.get_role(id)

    def reset_ids(self):
        """Fix the ids of all color and themes so they match the guild."""
        for color in self.colors:
            color.guild_id = self.id
        for theme in self.themes:
            theme.guild_id = self.id

    async def clear_colors(self):
        """Remove all colors and associated roles from the guild."""
        for color in self.colors:
            # deletes role associated with color
            if color.role_id:
                try:
                    role = bot.get_guild(self.id).get_role(color.role_id)
                    await role.delete()
                except:
                    color.role_id = None
        self.colors.clear()

    def get_color(self, attr, value):
        """Search for a color in the guild via attribute.

        Args:
            attr (str): The name of the attribute of the color
            value: The name of the value to match to each color attribute
        """
        for color in self.colors:
            if color.__getattribute__(attr) == value:
                return color

    def get_theme(self, attr, value):
        """Search for a Theme in the guild via attribute.

        Args:
            attr (str): The name of the attribute of the color
            value: The name of the value to match to each color attribute
        """
        for theme in self.themes:
            if theme.__getattribute__(attr) == value:
                return theme

    def random_color(self):
        """Return a random color object."""
        try:
            return random.choice(self.colors)
        except IndexError:
            pass

    def get_color_role(self, user):
        """
        Get a users color role if it exists.

        Args:
            user (discord.User): The user to get roles from
            guild (discord.Guild): The guild to use

        Returns:
            role = discord.Role: The color role
        """
        ids = {role.id for role in user.roles}
        role = ids & {color.role_id for color in self.colors if color.role_id}
        if role:
            return self.get_role(role.pop())

    def draw_colors(self):
        """Draw colored boxes based on a colors.

        Returns:
            A byte array of the image
        """
        sep = os.path.sep  # separator for cross-platform

        rows = math.ceil(len(self.colors) / 3)  # amt of rows needed
        rows = 1 if not rows else rows
        row_height = 50
        column_width = 300
        columns = 3
        discord = (54, 57, 63)  # discord background color

        img = Image.new(mode='RGB',
                        size=(columns * column_width, rows * row_height),
                        color=discord)
        draw = ImageDraw.Draw(img)  # set image for drawing
        fnt = ImageFont.truetype(
            font=f'.{sep}assets{sep}Roboto.ttf', size=30)

        # draws and labels boxes
        for i, color in enumerate(self.colors):

            # draw boxes
            rem = i % 3  # 0,1,2 repeating
            div = i//3  # increment every 3 elements
            x1 = column_width * rem
            x2 = row_height * div
            y1 = column_width * (rem+1)
            y2 = row_height*(div+1)
            draw.rectangle([x1, x2, y1, y2], fill=color.rgb,
                           outline=discord, width=2)

            W, H = column_width*rem, row_height*div+10  # origin to draw boxes
            msg = f"{color.index}. {color.name}"
            w, _ = draw.textsize(msg, fnt)  # width of text

            # cut text until it fits
            text_size_limit = column_width - (column_width/10)
            while w > text_size_limit:
                msg = msg[:-2]
                w, _ = draw.textsize(msg, fnt)
                if w <= text_size_limit:
                    msg = msg + "..."

            # Make text readable
            r, g, b = color.rgb
            luminance = (0.299 * r + 0.587 * g + 0.114 * b)/255
            text_color = (0, 0, 0) if luminance > 0.5 else (255, 255, 255)

            # Draw text on boxes
            x = (column_width-w)/2 + W
            y = H
            draw.text((x, y), msg, font=fnt, fill=text_color)  # draw text

        # draw if there are no colors
        if not self.colors:
            msg = "No active colors"
            w, _ = draw.textsize(msg, fnt)
            draw.text(((900-w) / 2, 0), "No active colors",
                      font=fnt, fill=(255, 255, 255))

        # return binary data
        imgByteArr = io.BytesIO()
        img.save(imgByteArr, format='PNG')
        imgByteArr = imgByteArr.getvalue()
        return imgByteArr

    def draw_themes(self):
        """
        Draws guild themes.

        Returns:
            imgByteArray (bytes): byte array of the image
        """
        color_height = 44  # height of color boxes
        cont_height = 112 + 7  # container height
        canvas_width = 900
        padding_above_text = 20
        padding_below_text = 10
        box_margin = 5

        rows = 1 if not self.themes else len(self.themes)

        img = Image.new(mode='RGB',
                        size=(canvas_width, cont_height * rows),
                        color=(54, 57, 63))
        draw = ImageDraw.Draw(img)  # set image for drawing

        # set font
        fnt = ImageFont.truetype(
            f'.{os.path.sep}assets{os.path.sep}Roboto.ttf',
            size=40)

        white = (255, 255, 255)  # white

        # draws themes
        for i, theme in enumerate(self.themes):
            # draw text
            msg = f"{theme.index}. {theme.name}"
            text_width, text_height = draw.textsize(msg, fnt)

            # text coords
            x = (canvas_width/2)-(text_width/2)  # center
            y = i * cont_height + padding_above_text

            text_height += padding_above_text + padding_below_text

            draw.text((x, y), msg, font=fnt, fill=white)

            width_of_rect = canvas_width/len(theme.colors)

            # draw color preview
            for j, color in enumerate(theme.colors, 0):
                # top left corner
                x0 = j * width_of_rect
                y0 = i * cont_height + text_height

                # bottom right corner
                x1 = x0 + width_of_rect - box_margin
                y1 = y0 + color_height

                draw.rectangle([(x0, y0), (x1, y1)], fill=color.rgb)

        # different drawing if no themes
        if not self.themes:
            draw.text((20, 0), f"No Themes", font=fnt, fill=white)

        # return binary data
        imgByteArr = io.BytesIO()
        img.save(imgByteArr, format='PNG')
        imgByteArr = imgByteArr.getvalue()
        return imgByteArr

    def find_color(self, query, threshold=90):
        """Find a color in the guild's colors based on index or name.

        Args:
            query (str): The term to search for
            threshold (int): The matching threshold 0-100
        """
        # random color
        if query == "":
            return self.random_color()

        # get color by index
        elif query.isdigit() and 0 < int(query) < len(self.colors) + 1:
            return self.get_color('index', int(query))

        # get color by name
        else:
            name, rating = process.extractOne(
                query, [color.name for color in self.colors])
            if rating >= threshold:
                return self.get_color('name', name)

    def find_theme(self, query, threshold=80):
        """Find a theme in the guild's themes based on index or name

        Args:
            query (str): The term to search for
            threshold (int): The matching threshold 0-100
        Returns:
            (Theme): returns a theme object if found
            None (NoneType): returns None if theme not found
        """
        # get theme by index
        if query.isdigit() and 0 < int(query) < len(self.themes) + 1:
            return self.get_theme('index', int(query))

        # get theme by name
        else:
            best_theme, rating = process.extractOne(
                query, [theme.name for theme in self.themes])
            if rating >= threshold:
                return self.get_theme('name', best_theme)

    def find_user(self, query, message=None, threshold=80):
        """Search for a user in the guild with a query.

        Args:
            message (discord.Message): the message with command
            query (str): the name to search for
            guild (discord.Guild): the guild the member is in
            threshold (int): the fuzzy matching threshold

        Returns:
            discord.User: the user if found
        """
        # check mentions
        if message and message.mentions:
            user = message.mentions[0]

        # try fuzzy matching
        else:
            member_names = (member.name for member in self.members)
            best_user, rating = process.extractOne(query, member_names)
            for member in self.members:
                if member.name == best_user:
                    if rating <= threshold:
                        user = None
                    else:
                        user = member
                        break
        return user

    def to_json(self):
        """Convert Guild object to valid JSON."""
        return {
            "name": self.name,
            "id": self.id,
            "prefix": self.prefix,
            "welcome_channel": self.welcome_channel_id,
            "disabled_channels": list(self.disabled_channel_ids),
            "theme_limit": self.theme_limit,
            "color_limit": self.color_limit,
            "themes": [theme.to_json() for theme in self.themes],
            "colors": [color.to_json() for color in self.colors]
        }

    @classmethod
    def get(cls, id):
        """Find guild in the dictionary."""
        return cls._guilds.get(id)

    @staticmethod
    def from_json(data):
        """Convert valid JSON to guild object."""
        return Guild(
            id=data["id"],
            prefix=data['prefix'],
            welcome_channel_id=data["welcome_channel"],
            disabled_channel_ids=set(data["disabled_channels"]),
            theme_limit=data["theme_limit"],
            color_limit=data["color_limit"],
            themes=[Theme.from_json(theme) for theme in data["themes"]],
            colors=[Color.from_json(color) for color in data["colors"]])


class Color():
    """
    A color object that stores color data.

    Args:
        name(str): The name of the color
        hexcode(str): The hexcode of the color
        guild_id(int): The id of the guild the color belongs to
        role_id(int): the discord role id of the color if created
        member_ids(set): set of discord ids for members with this role

    Attributes:
        name(str): The name of the color
        hexcode(str): The hexcode of the color
        rgb(tuple of int): The rgb values of the color
        guild_id(int): The id of the guild the color belongs to
        role_id(int): the discord role id of the color if created
    """

    def __init__(self, name, hexcode, guild_id, role_id=None, member_ids=set()):
        self.name = name
        self.hexcode = hexcode
        self.guild_id = guild_id
        self.role_id = role_id
        self.member_ids = member_ids

    @property
    def rgb(self):
        """Convert hexcode into RGB tuple."""
        return hex_to_rgb(self.hexcode)

    @property
    def guild(self):
        return Guild.get(self.guild_id)

    @property
    def index(self):
        return self.guild.colors.index(self) + 1

    @property
    def members(self):
        """Generator for members that occupy a color"""
        return (member for member in self.guild.members
                if member.id in self.member_ids)

    def __str__(self):
        return self.name

    def __repr__(self):
        """Method for cleaner printing."""
        has_role = bool(self.role_id)
        return (f"{self.index}.{self.name} {self.hexcode} "
                f"Active:{has_role} Members:{len(self.member_ids)}")

    async def delete(self):
        """Remove a color from the guild. Deletes associated roles"""
        self.guild.colors.remove(self)

        # deletes role associated with color if specified
        if self.role_id:
            print(f"Deleteing {self.name} role")
            role = self.guild.get_role(self.role_id)
            if role:
                await role.delete()
            self.role_id = None

    def to_json(self):
        """Convert Color object to valid JSON."""
        return {
            "name": self.name,
            "hexcode": self.hexcode,
            "guild_id": self.guild_id,
            "role_id": self.role_id,
            "members": list(self.member_ids)
        }

    @staticmethod
    def from_json(color):
        """Create Color object from valid JSON"""
        return Color(
            name=color["name"],
            hexcode=color["hexcode"],
            guild_id=color["guild_id"],
            role_id=color["role_id"],
            member_ids=set(color["members"]))


class Theme():
    """An object that stores a list of color objects with name and description

    Args:
        name(str): The name of the theme
        guild_id(int): The id of the guild the color belongs to
        description(str): the description of the theme

    Attributes:
        name(str): The name of the theme
        description(str): the description of the theme
        guild_id(int): The id of the guild the color belongs to
        color(list of Color): a list of Color belonging to the theme
        active(boolean): Determines if theme is in use(unused)
        index(int): The location in the list of themes in the guild
    """

    def __init__(self, name, guild_id, description="", colors=[]):
        self.name = name
        self.guild_id = guild_id
        self.description = description
        self.colors = colors

    @property
    def guild(self):
        return Guild.get(self.guild_id)

    @property
    def index(self):
        return self.guild.themes.index(self) + 1

    def delete(self):
        """Removes theme from guild"""
        self.guild.themes.remove(self)

    def activate(self):
        """adds theme colors to the colors list of the guild"""
        guild = self.guild
        new_colors = copy.deepcopy(self.colors)
        guild.colors = new_colors

    def to_json(self):
        """Convert Color object to valid JSON."""
        return {
            "name": self.name,
            "description": self.description,
            "guild_id": self.guild_id,
            "colors": [color.to_json() for color in self.colors],
        }

    @staticmethod
    def from_json(theme):
        """Create Theme object from valid JSON"""
        return Theme(
            name=theme["name"],
            description=theme["description"],
            guild_id=theme["guild_id"],
            colors=[Color.from_json(color) for color in theme["colors"]])
