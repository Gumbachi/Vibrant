import copy
import io
import json
import math
import os
import random
from os.path import sep

import database as db
import discord
from discord.ext import commands
from rapidfuzz import process
from PIL import Image, ImageDraw, ImageFont

from vars import bot
from utils import hex_to_rgb
import authorization as auth
from expiringdict import ExpiringDict


class Guild:
    """Guild object that stores preferences for a guild the bot is in

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
    _cache = ExpiringDict(max_len=100, max_age_seconds=3600)

    def __init__(self, id, **kwargs):
        self.name = str(bot.get_guild(id))
        self.id = id
        self.prefix = kwargs.get("prefix", "$")
        self.welcome_channel_id = kwargs.get("welcome_channel_id", None)
        self.disabled_channel_ids = kwargs.get("disabled_channel_ids", set())
        self.theme_limit = kwargs.get("theme_limit", 3)
        self.color_limit = kwargs.get("color_limit", 25)
        self.themes = kwargs.get("themes", [])
        self.colors = kwargs.get("colors", [])
        self.heavy_command_active = None
        self.waiting_on_hexcode = {}

        Guild._cache[id] = self  # add guild to the dict

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

    def __str__(self):
        """String that represents the guild."""
        return (f"Name: {self.name}\nID: {self.id}\nPrefix: {self.prefix}\n"
                f"Welcome: {self.welcome_channel.mention}\n"
                f"Disabled Channels: {len(self.disabled_channel_ids)}/{len(self.discord_guild.text_channels)}\n"
                f"Colors: {len(self.colors)}/{self.color_limit}\n"
                f"Themes: {len(self.themes)}/{self.theme_limit}\n"
                f"Members: {len(self.members)}")

    @classmethod
    def get(cls, id):
        """Find guild in the dictionary or db."""
        try:
            return cls._cache[id]
        except KeyError:
            data = db.find_guild(id)
            if data:
                return Guild.from_json(data)
            else:
                print("Missing")
                raise auth.MissingGuild()


######################### COLOR/THEME MANAGEMENT #########################


    async def clear_colors(self):
        """Remove all colors and associated roles from the guild."""
        for color in self.colors:
            # deletes role associated with color
            if color.role_id:
                try:
                    role = self.get_role(color.role_id)
                    await role.delete()
                except:
                    color.role_id = None
        self.colors.clear()

    def erase_user(self, user_id):
        """Clears all traces of a user"""
        for color in self.colors:
            color.member_ids.discard(user_id)

        for theme in self.themes:
            for color in theme.colors:
                color.member_ids.discard(user_id)

######################### GETTERS #########################

    def get_role(self, id):
        """Get a discord role from a given ID."""
        discord_guild = self.discord_guild
        if discord_guild:
            return discord_guild.get_role(id)

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

######################### FINDERS #########################

    def find_color(self, query, threshold=90):
        """Find a color in the guild's colors based on index or name.

        Args:
            query (str): The term to search for
            threshold (int): The matching threshold 0-100
        """
        # random color
        if query == "":
            return random.choice(self.colors)

        # get color by index
        elif query.isdigit() and 0 < int(query) < len(self.colors) + 1:
            return self.get_color('index', int(query))

        # get color by name
        else:
            match = process.extractOne(
                query, [color.name for color in self.colors],
                score_cutoff=threshold)
            if match:
                return self.get_color('name', match[0])

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
            match = process.extractOne(
                query, [theme.name for theme in self.themes],
                score_cutoff=threshold)
            if match:
                return self.get_theme('name', match[0])

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
            return message.mentions[0]

        # try fuzzy matching
        member_names = [member.name for member in self.members]
        match = process.extractOne(query, member_names,
                                   score_cutoff=threshold)

        if not match:
            return None

        best_user = match[0]
        for member in self.members:
            if member.name == best_user:
                return member

######################### IMPORT/EXPORT #########################

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

######################### DRAWING #########################

    def draw_colors(self):
        """Draw colored boxes based on a colors.

        Returns:
            A byte array of the image
        """
        rows = math.ceil(len(self.colors) / 3)  # amt of rows needed
        row_height = 50
        column_width = 300
        columns = 3

        img = Image.new(mode='RGBA',
                        size=(columns * column_width, rows * row_height),
                        color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)  # set image for drawing
        fnt = ImageFont.truetype(
            font=f".{sep}assets{sep}Roboto.ttf", size=30)

        # draws and labels boxes
        for i, color in enumerate(self.colors):

            # draw boxes
            rem = i % 3  # 0,1,2 repeating
            div = i//3  # increment every 3 elements
            x1 = column_width * rem
            x2 = row_height * div
            y1 = column_width * (rem+1)
            y2 = row_height * (div+1)
            draw.rectangle([x1, x2, y1, y2], fill=color.rgb,
                           outline=(0, 0, 0, 0), width=2)

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

        return img

    def draw_themes(self):
        """
        Draws guild themes.

        Returns:
            list of Image: the list of images segmented by 5
        """

        color_height = 44  # height of color boxes
        cont_height = 112 + 7  # container height
        canvas_width = 900
        padding_above_text = 20
        padding_below_text = 10
        box_margin = 5

        fnt = ImageFont.truetype(f'assets{sep}Roboto.ttf', size=40)

        theme_images = []

        for x in range(math.ceil(len(self.themes)/5)):
            # x is 1, 2, 3

            start = x * 5
            end = len(self.themes) if start + \
                5 > len(self.themes) else start + 5

            cut_themes = self.themes[start:end]
            rows = len(cut_themes)

            img = Image.new(mode='RGBA',
                            size=(canvas_width, cont_height * rows),
                            color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)  # set image for drawing

            # draws themes
            for i, theme in enumerate(cut_themes):
                # draw text
                msg = f"{theme.index}. {theme.name}"
                text_width, text_height = draw.textsize(msg, fnt)

                # text coords
                x = (canvas_width/2)-(text_width/2)  # center
                y = i * cont_height + padding_above_text

                text_height += padding_above_text + padding_below_text

                draw.text((x, y), msg, font=fnt, fill=(255, 255, 255))

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
            theme_images.append(img)
        return theme_images


class Color(commands.Converter):
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

    def __init__(self, name, hexcode, guild_id, **kwargs):
        self.name = name
        self.hexcode = hexcode
        self.guild_id = guild_id
        self.role_id = kwargs.get("role_id", None)
        self.member_ids = kwargs.get("member_ids", set())

    @property
    def rgb(self):
        """Convert hexcode into RGB tuple."""
        return hex_to_rgb(self.hexcode)

    @property
    def guild(self):
        return Guild.get(self.guild_id)

    @property
    def index(self):
        try:
            return self.guild.colors.index(self) + 1
        except ValueError:
            return 1

    @property
    def members(self):
        """Generator for members that occupy a color"""
        return (member for member in self.guild.members
                if member.id in self.member_ids)

    @property
    def role(self):
        """Get associated discord role."""
        if self.role_id:
            role = self.guild.get_role(self.role_id)
            if not role:
                self.role_id = None
            return role

    def to_discord(self):
        """Convert color to discord.Color."""
        return discord.Color.from_rgb(*self.rgb)

    def __str__(self):
        """String representing the color"""
        return f"{self.index}.{self.name} ({self.hexcode}) ({len(self.member_ids)})"

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


class Theme:
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

    def __init__(self, name, guild_id, **kwargs):
        self.name = name
        self.guild_id = guild_id
        self.description = kwargs.get("description", name)
        self.colors = kwargs.get("colors", [])

    def __str__(self):
        """String representing the theme"""
        return f"{self.index}.{self.name} ({len(self.colors)} colors)"

    @property
    def guild(self):
        return Guild.get(self.guild_id)

    @property
    def index(self):
        return self.guild.themes.index(self) + 1

    def delete(self):
        """Removes theme from guild"""
        try:
            self.guild.themes.remove(self)
        except ValueError:
            pass

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
