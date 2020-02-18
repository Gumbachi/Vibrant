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

    def __init__(self, id, prefix='$', welcome_channel=None,
                 disabled_channels=set(), theme_limit=3, color_limit=25,
                 themes=[], colors=[]):
        if bot.get_guild(id):
            self.name = bot.get_guild(id).name
        else:
            self.name = "ABANDONED"
        self.id = id
        self.prefix = prefix
        self.welcome_channel = welcome_channel
        self.disabled_channels = disabled_channels
        self.theme_limit = theme_limit
        self.color_limit = color_limit
        self.themes = themes
        self.colors = colors
        Guild._guilds[id] = self # add guild to the dict


    def __repr__(self):
        """
        Output a string that represents the guild object and
        cleanly displays data
        """
        out = (f"Name: {self.name}\nID: {self.id}\nPrefix: {self.prefix}\n"
               f"Welcome: {self.welcome_channel}\n"
               f"Theme Limit: {self.theme_limit}\n"
               f"Color Limit: {self.color_limit}\n"
               f"Disabled Channels\n")
        for channel in self.disabled_channels:
            out += f"    {channel}\n"

        out += "Colors\n"
        for color in self.colors:
            out += f"    {repr(color)}\n"

        return out


    def get_role(self, role_id):
        """get a discord.Role."""
        guild = bot.get_guild(self.id) # discord.Guild
        if guild:
            return guild.get_role(role_id)

    def fix_ids(self):
        """Fix the ids so they line up"""
        for color in self.colors:
            color.guild_id = self.id
        for theme in self.themes:
            theme.guild_id = self.id


    # def verify_color_members(self):
    #     """Verify users only show up once"""
    #     acc_for = []
    #     for color in self.colors:
    #         for id in color.members:
    #             if id in acc_for:
    #                 color.members.discard(id)
    #             else:
    #                 acc_for.append(id)

    async def clear_colors(self):
        """Remove all colors from the guild."""
        for color in self.colors:
            # deletes role associated with color
            if color.role_id:
                try:
                    role = bot.get_guild(self.id).get_role(color.role_id)
                    await role.delete()
                except:
                    self.role_id = None
        self.colors.clear()


    def get_color(self, attr, value):
        """
        Search for a color in the guild via attribute.

        Args:
            attr (str): The name of the attribute of the color
            value: The name of the value to match to each color attribute

        Returns:
            color (Color): if color is found returns the Color object
        """
        for color in self.colors:
            if color.__getattribute__(attr) == value:
                return color


    def get_theme(self, attr, value):
        """
        Search for a color in the guild via attribute.

        Args:
            attr (str): The name of the attribute of the color
            value: The name of the value to match to each color attribute

        Returns:
            theme (Theme): if theme is found returns the Theme object
        """
        for theme in self.themes:
            if theme.__getattribute__(attr) == value:
                return theme


    def rand_color(self):
        """Return a random color object."""
        try:
            return random.choice(self.colors)
        except IndexError:
            return None


    def get_welcome(self):
        """Return discord.Channel object of welcome channel."""
        guild = bot.get_guild(self.id)
        return guild.get_channel(self.welcome_channel)


    def get_enabled(self):
        """Return a list of discord.Channel objects of enabled channels."""
        guild = bot.get_guild(self.id)
        if guild:
            return [channel for channel in guild.text_channels
                    if channel.id not in self.disabled_channels]
        else:
            return []


    def get_disabled(self):
        """Return a list of discord.Channel objects of disabled channels."""
        guild = bot.get_guild(self.id)
        if guild:
            return [channel for channel in guild.text_channels
                    if channel.id in self.disabled_channels]
        else:
            return []


    def list_colors_by(self, attr):
        """Compile a list of an attribute."""
        return [color.__getattribute__(attr) for color in self.colors]


    def list_themes_by(self, attr):
        """Compile a list of an attribute."""
        l = [theme.__getattribute__(attr) for theme in self.themes]
        return list(filter(None, l)) # filter out None values


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
        role = ids & set(self.list_colors_by("role_id"))
        if role:
            return self.get_role(role.pop())


    def draw_colors(self):
        """
        Draw colored boxes based on a colors.

        Returns:
            A byte array of the image
        """
        sep = os.path.sep #separator for cross-platform

        rows = math.ceil(len(self.colors) / 3) #amt of rows needed
        rows = 1 if not rows else rows
        row_height = 50
        column_width = 300
        columns = 3
        discord = (54,57,63) # discord background color

        img = Image.new(mode='RGB',
                        size=(columns * column_width, rows * row_height),
                        color=discord)
        draw = ImageDraw.Draw(img) # set image for drawing
        fnt = ImageFont.truetype(
            font=f'.{sep}assets{sep}Roboto.ttf', size=30)

        #draws and labels boxes
        for i, color in enumerate(self.colors):

            #draw boxes
            rem = i % 3 # 0,1,2 repeating
            div = i//3 # increment every 3 elements
            x1 = column_width * rem
            x2 = row_height * div
            y1 = column_width * (rem+1)
            y2 = row_height*(div+1)
            draw.rectangle([x1, x2, y1, y2], fill=color.rgb(),
                           outline=discord, width=2)

            W, H = column_width*rem, row_height*div+10 #origin to draw boxes
            msg = f"{color.index}. {color.name}"
            w, _ = draw.textsize(msg, fnt) #width of text

            #cut text until it fits
            text_size_limit = column_width - (column_width/10)
            while w > text_size_limit:
                msg = msg[:-2]
                w, _ = draw.textsize(msg, fnt)
                if w <= text_size_limit:
                    msg = msg + "..."

            #Make text readable
            r, g, b = color.rgb()
            luminance = (0.299 * r + 0.587 * g + 0.114 * b)/255
            text_color = (0, 0, 0) if luminance > 0.5 else (255, 255, 255)

            #Draw text on boxes
            x = (column_width-w)/2 + W
            y = H
            draw.text((x, y), msg, font=fnt, fill=text_color) #draw text

        #draw if there are no colors
        if not self.colors:
            msg = "No active colors"
            w, _ = draw.textsize(msg, fnt)
            draw.text(((900-w) / 2, 0), "No active colors",
                      font=fnt, fill=(255,255,255))

        #return binary data
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
        color_height = 44 # height of color boxes
        cont_height = 112 + 7 # container height
        canvas_width = 900
        padding_above_text = 20
        padding_below_text = 10
        box_margin = 5

        rows = 1 if not self.themes else len(self.themes)

        img = Image.new(mode='RGB',
                        size=(canvas_width, cont_height * rows),
                        color=(54,57,63))
        draw = ImageDraw.Draw(img) # set image for drawing

        # set font
        fnt = ImageFont.truetype(
            f'.{os.path.sep}assets{os.path.sep}Roboto.ttf',
            size=40)

        white = (255,255,255) # white

        # draws themes
        for i, theme in enumerate(self.themes):

            #draw text
            msg = f"{theme.index}. {theme.name}"
            text_width, text_height = draw.textsize(msg, fnt)

            # text coords
            x = (canvas_width/2)-(text_width/2) # center
            y = i * cont_height + padding_above_text

            text_height += padding_above_text + padding_below_text

            draw.text((x, y), msg, font=fnt, fill=white)

            width_of_rect = canvas_width/len(theme.colors)

            #draw color preview
            for j, color in enumerate(theme.colors, 0):
                rgb = color.rgb()

                # top left corner
                x0 = j * width_of_rect
                y0 = i * cont_height + text_height

                # bottom right corner
                x1 = x0 + width_of_rect - box_margin
                y1 = y0 + color_height

                draw.rectangle([(x0, y0), (x1, y1)], fill=rgb)

        # different drawing if no themes
        if not self.themes:
            draw.text((20, 0), f"No Themes", font=fnt, fill=white)

        #return binary data
        imgByteArr = io.BytesIO()
        img.save(imgByteArr, format='PNG')
        imgByteArr = imgByteArr.getvalue()
        return imgByteArr


    def discord_guild(self):
        """Get the discord.guild that matches this one"""
        try:
            return bot.get_guild(self.id)
        except:
            return None


    def find_color(self, query, threshold=90):
        """
        Find a color in the guild's colors based on index or name.

        Args:
            query (str): The term to search for
            threshold (int): The matching threshold 0-100
        Returns:
            (Color): returns a color object if found
            None (NoneType): returns None if color not found
        """
        # random color
        if query == "":
            return self.rand_color()

        # get color by index
        elif query.isdigit() and 0 < int(query) < len(self.colors) + 1:
            return self.get_color('index', int(query))

        # get color by name
        else:
            name, rating = process.extractOne(query, self.list_colors_by("name"))
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
            best_theme, rating = process.extractOne(query, self.list_themes_by("name"))
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

        guild = self.discord_guild()

        # check mentions
        if message and message.mentions:
            user = message.mentions[0]

        # try fuzzy matching
        else:
            member_names = [member.name for member in guild.members]
            best_user, rating = process.extractOne(query, member_names)
            for member in guild.members:
                if member.name == best_user:
                    if rating <= threshold:
                        user = None
                    else:
                        user = member
                        break
        return user


    def reindex_colors(self):
        """Reindexes all of the guilds colors """
        for i, color in enumerate(self.colors, 1):
            color.index = i


    def reindex_themes(self):
        """Reindexes all of the guilds themes """
        for i, theme in enumerate(self.themes, 1):
            theme.index = i


    def to_json(self):
        """Convert Guild object to valid JSON."""
        return {
            "name": self.name,
            "id": self.id,
            "prefix": self.prefix,
            "welcome_channel": self.welcome_channel,
            "disabled_channels": list(self.disabled_channels),
            "theme_limit": self.theme_limit,
            "color_limit": self.color_limit,
            "themes": [theme.to_json() for theme in self.themes],
            "colors": [color.to_json() for color in self.colors]
        }


    @classmethod
    def get(cls, id):
        """Finds guild in the dictionary"""
        return cls._guilds.get(id)


    @classmethod
    def from_json(cls, data):
        """Convert valid JSON to guild object."""
        return cls(
            id=data["id"],
            prefix=data['prefix'],
            welcome_channel=data["welcome_channel"],
            disabled_channels=set(data["disabled_channels"]),
            theme_limit=data["theme_limit"],
            color_limit=data["color_limit"],
            themes=[Theme.from_json(theme) for theme in data["themes"]],
            colors=[Color.from_json(color) for color in data["colors"]])


class Color():
    """A color object that stores color data

    Args:
        name (str): The name of the color
        hexcode (str): The hexcode of the color
        guild_id (int): The id of the guild the color belongs to
        role_id (int): the discord role id of the color if created

    Attributes:
        name (str): The name of the color
        hexcode (str): The hexcode of the color
        rgb (tuple of int): The rgb values of the color
        guild_id (int): The id of the guild the color belongs to
        role_id (int): the discord role id of the color if created
    """
    def __init__(self, name, hexcode, guild_id, role_id=None, members=set()):
        self.name = name
        self.hexcode = hexcode
        self.guild_id = guild_id
        self.role_id = role_id
        self.members = members
        if self.find_guild():
            self.index = len(self.find_guild().colors) + 1
        else:
            self.index = 1


    def __repr__(self):
        """Method for cleaner printing."""
        has_role = True if self.role_id else False
        return (f"{self.index}.{self.name} {self.hexcode} "
                f"Active:{has_role} Members:{len(self.members)}")


    def rgb(self):
        """Convert hexcode into RGB tuple."""
        return hex_to_rgb(self.hexcode)


    async def delete(self, delete_role=True):
        """
        Remove a color from the colors attribute of a guild
        and deletes any roles associated with the color as well
        as reindexing the colors in the guild.
        """
        colors = self.find_guild().colors
        colors.remove(self)

        # deletes role associated with color if specified
        if delete_role and self.role_id:
            print(f"Removing {self.name}")
            role = self.find_guild().get_role(self.role_id)
            if role:
                await role.delete()
            self.role_id = None


    def find_guild(self):
        """Find and return the Guild object the color belongs to"""
        id = int(self.guild_id)
        return Guild._guilds.get(id)


    def to_json(self):
        """Convert Color object to valid JSON."""
        return {
            "name": self.name,
            "hexcode": self.hexcode,
            "guild_id": self.guild_id,
            "role_id": self.role_id,
            "members": list(self.members)
        }


    @classmethod
    def from_json(cls, color):
        """Create Color object from valid JSON"""
        return cls(
            name=color["name"],
            hexcode=color["hexcode"],
            guild_id=color["guild_id"],
            role_id=color["role_id"],
            members=set(color["members"]))


class Theme():
    """An object that stores a list of color objects with name and description

    Args:
        name (str): The name of the theme
        guild_id (int): The id of the guild the color belongs to
        description (str): the description of the theme

    Attributes:
        name (str): The name of the theme
        description (str): the description of the theme
        guild_id (int): The id of the guild the color belongs to
        color (list of Color): a list of Color belonging to the theme
        active (boolean): Determines if theme is in use (unused)
        index (int): The location in the list of themes in the guild
    """
    def __init__(self, name, guild_id, description="", colors=[]):
        self.name = name
        self.guild_id = guild_id
        self.description = description
        self.colors = colors
        if self.find_guild():
            self.index = len(self.find_guild().themes) + 1
        else:
            self.index = 1


    def find_guild(self):
        """Find and return the Guild object the theme belongs to"""
        return Guild._guilds.get(int(self.guild_id))


    def delete(self):
        """Removes theme from guild and reindexes themes"""
        guild = self.find_guild()
        guild.themes.remove(self)

        guild.reindex_themes()


    def activate(self):
        """adds theme colors to the colors list of the guild"""
        guild = self.find_guild()
        new_colors = copy.deepcopy(self.colors)
        guild.colors = new_colors
        guild.reindex_colors()


    def rand_color(self):
        """Returns a random color object"""
        try:
            return random.choice(self.colors)
        except IndexError:
            return None


    def to_json(self):
        """Convert Color object to valid JSON."""
        return {
            "name": self.name,
            "description": self.description,
            "guild_id": self.guild_id,
            "colors": [color.to_json() for color in self.colors],
        }


    @classmethod
    def from_json(cls, theme):
        """Create Theme object from valid JSON"""
        return cls(
            name=theme["name"],
            description=theme["description"],
            guild_id=theme["guild_id"],
            colors=[Color.from_json(color) for color in theme["colors"]])
