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
import functions as fn


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
                 disabled_channels=[], theme_limit=3, color_limit=25):
        if not bot.get_guild(id):
            self.name = "ABANDONED"
        else:
            self.name = bot.get_guild(id).name
        self.id = id
        self.prefix = prefix
        self.welcome_channel = welcome_channel
        self.disabled_channels = disabled_channels
        self.colors = []
        self.themes = []
        self.theme_limit = theme_limit
        self.color_limit = color_limit
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
        """returns a discord.Role"""
        guild = bot.get_guild(self.id) # discord.Guild
        if guild:
            return guild.get_role(role_id)


    async def clear_colors(self):
        roles_to_delete = self.get_color_role_ids()
        for id in roles_to_delete:
            try:
                await self.get_role(id).delete()
            except:
                pass
        self.colors = []


    def get_color(self, attr, value):
        """Search for a color in the guild via attribute

        Args:
            attr (str): The name of the attribute of the color
            value: The name of the value to match to each color attribute

        Returns:
            color (Color): if color is found returns the Color object
            None (NoneType): returns None if color is not found
        """
        for color in self.colors:
            if color.__getattribute__(attr) == value:
                return color


    def get_theme(self, attr, value):
        """Search for a color in the guild via attribute

        Args:
            attr (str): The name of the attribute of the color
            value: The name of the value to match to each color attribute

        Returns:
            theme (Theme): if theme is found returns the Theme object
            None (NoneType): returns None if color is not found
        """
        for theme in self.themes:
            if theme.__getattribute__(attr) == value:
                return theme


    def rand_color(self):
        """Returns a random color object"""
        try:
            color = random.choice(self.colors)
        except IndexError:
            return None
        return color


    def get_welcome(self):
        """returns discord.Channel object of welcome channel"""
        guild = bot.get_guild(self.id)
        return guild.get_channel(self.welcome_channel)


    def get_enabled(self):
        """returns discord.Channel objects of enabled channels"""
        guild = bot.get_guild(self.id)
        if guild:
            return [channel for channel in guild.text_channels
                    if channel.id not in self.disabled_channels]
        else:
            return []


    def get_disabled(self):
        """returns discord.Channel objects of disabled channels"""
        guild = bot.get_guild(self.id)
        if guild:
            return [channel for channel in guild.text_channels
                    if channel.id in self.disabled_channels]
        else:
            return []


    def color_names(self):
        """Generates a list of names of the colors"""
        return [color.name for color in self.colors]


    def theme_names(self):
        """Generates a list of names of the themes"""
        return [theme.name for theme in self.themes]


    def get_color_role_ids(self):
        """gets a list of roles created by the bot

        Args:
            guild (discord.Guild): The guild to use

        Returns:
            list of int: The role ids
        """
        return [color.role_id for color in self.colors if color.role_id]


    def get_color_role(self, user):
        """gets a list of roles created by the bot

        Args:
            user (discord.User): The user to get roles from
            guild (discord.Guild): The guild to use

        Returns:
            discord.Role: The color role
            None: If user is uncolored
        """
        color_roles = self.get_color_role_ids()
        for role in user.roles:
            if role.id in color_roles:
                return self.get_role(role.id)
        return None


    def draw_colors(self):
        """Draws colored boxes based on a colors

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
            font=f'.{sep}assets{sep}Montserrat-Regular.ttf', size=30)

        #draws and labels boxes
        for i, color in enumerate(self.colors):

            #draw boxes
            rem = i % 3 # 0,1,2 repeating
            div = i//3 # increment every 3 elements
            x1 = column_width * rem
            x2 = row_height * div
            y1 = column_width * (rem+1)
            y2 = row_height*(div+1)
            draw.rectangle([x1, x2, y1, y2], fill=color.rgb,
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
            r, g, b = color.rgb
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
        """Draws guild themes

        Returns:
            imgByteArray(bytes): byte array of the image
        """
        row_height = 60
        canvas_width = 900
        text_width = 250
        margin = 5

        cols = 1 if not self.themes else len(self.themes)

        img = Image.new(mode='RGB',
                        size=(canvas_width, cols * row_height),
                        color=(54,57,63))
        draw = ImageDraw.Draw(img) # set image for drawing
        fnt = ImageFont.truetype(
            f'.{os.path.sep}assets{os.path.sep}Montserrat-Regular.ttf',
            size=30)#set font

        text_color = (255,255,255) # white


        # draws themes
        for i, theme in enumerate(self.themes):

            #draw text
            draw.text((20, i*row_height + 15), f"{theme.name}: ",
                      font=fnt, fill=text_color) # draw text on rectangles
            w, _ = draw.textsize(f"{theme.name}: ", fnt)
            w += 20 # include margin

            amt_colors = len(theme.colors)
            rem_space = canvas_width - text_width - margin
            width_of_rect = rem_space/amt_colors

            #draw color preview
            for j, color in enumerate(theme.colors, 0):
                rgb = color.rgb
                x1 = j * width_of_rect + text_width + margin
                x2 = i * row_height + margin
                y1 = (j+1) * width_of_rect + text_width
                y2 = (i+1) * row_height - margin
                draw.rectangle([x1, x2, y1, y2], fill=rgb)

        # different drawing if no themes
        if not self.themes:
            draw.text((20, 0), f"No Themes", font=fnt, fill=text_color)

        #return binary data
        imgByteArr = io.BytesIO()
        img.save(imgByteArr, format='PNG')
        imgByteArr = imgByteArr.getvalue()
        return imgByteArr


    def find_color(self, query, threshold=90):
        """Find a color in the guild's colors based on index or name

        Args:
            query (str): The term to search for
            threshold (int): The matching threshold 0-100
        Returns:
            (Color): returns a color object if found
            None (NoneType): returns None if color not found
        """
        if query == "":
            return self.rand_color() #random color
        elif query.isdigit() and 0 < int(query) < len(self.colors) + 1:
            return self.get_color('index', int(query))
        else:
            best_color, rating = process.extractOne(query, self.color_names())
            if rating <= threshold:
                return None
            else:
                return self.get_color('name', best_color)


    def find_theme(self, query, threshold=80):
        """Find a theme in the guild's themes based on index or name

        Args:
            query (str): The term to search for
            threshold (int): The matching threshold 0-100
        Returns:
            (Theme): returns a theme object if found
            None (NoneType): returns None if theme not found
        """
        if query.isdigit() and 0 < int(query) < len(self.themes) + 1:
            return self.get_theme('index', int(query))
        else:
            best_theme, rating = process.extractOne(query, self.theme_names())
            print(best_theme, rating)
            if rating < threshold:
                return None
            else:
                return self.get_theme('name', best_theme)


    def reindex(self):
        """Reindexes all of the guilds colors """
        for i, color in enumerate(self.colors, 1):
            color.index = i


    async def clear_empty_roles(self):
        """Deletes a guilds empty roles"""
        for color in self.colors:
            if color.role_id and not color.members:
                role = self.get_role(color.role_id)
                if role:
                    await role.delete()
                    print(f"deleted {role.name}")


    @classmethod
    def get_guild(cls, id):
        """Finds guild in the dictionary"""
        if id in cls._guilds.keys():
            return cls._guilds[id]


    @classmethod
    def from_json(cls, data):
        """Converts valid JSON to guild object"""
        guild = cls(data["id"], data['prefix'], data["welcome_channel"],
                    data["disabled_channels"], data["theme_limit"],
                    data["color_limit"])
        for color in data["colors"]:
            guild.colors.append(Color.from_json(color))
        for theme in data["themes"]:
            guild.themes.append(Theme.from_json(theme))
        return guild


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
    def __init__(self, name, hexcode, guild_id, role_id=None):
        self.name = name
        self.hexcode = hexcode
        self.rgb = fn.hex_to_rgb(hexcode)
        self.guild_id = guild_id
        self.role_id = role_id
        try:
            self.members = [member.id for member
                in bot.get_guild(guild_id).get_role(role_id).members]
        except:
            self.members = []
        self.index = len(self.find_guild().colors) + 1

    def __repr__(self):
        "Method for cleaner printing"
        has_role = True if self.role_id else False
        return (f"{self.index}.{self.name} {self.hexcode} "
                f"Active:{has_role} Members:{len(self.members)}")


    async def delete(self):
        """Removes a color from the colors attribute of a guild
        and deletes any roles associated with the color as well
        as reindexing the colors in the guild"""
        colors = self.find_guild().colors
        colors.remove(self)

        # reindex all other colors
        for i, color in enumerate(colors, 1):
            color.index = i

        # deletes role associated with color
        if self.role_id:
            try:
                role = self.find_guild().get_role(self.role_id)
                await role.delete()
            except:
                pass


    def find_guild(self):
        """Find and return the Guild object the color belongs to"""
        if self.guild_id in Guild._guilds.keys():
            return Guild._guilds[self.guild_id]


    @classmethod
    def from_json(cls, color):
        """Create Color object from valid JSON"""
        obj = cls(color["name"], color["hexcode"],
                   color["guild_id"], color["role_id"])
        if color["members"]:
            obj.members = color["members"]
        return obj


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
    def __init__(self, name, guild_id, description=""):
        self.name = name
        self.description = description
        self.guild_id = guild_id
        self.colors = []
        self.active = True
        self.index = len(self.find_guild().themes) + 1


    def find_guild(self):
        """Find and return the Guild object the theme belongs to"""
        if self.guild_id in Guild._guilds.keys():
            return Guild._guilds[self.guild_id]


    def delete(self):
        """Removes theme from guild and reindexes themes"""
        themes = self.find_guild().themes
        themes.remove(self)

        #reindex themes
        for i, theme in enumerate(themes, 1):
            theme.index = i


    def activate(self):
        """adds theme colors to the colors list of the guild"""
        guild = self.find_guild()
        new_colors = copy.deepcopy(self.colors)
        guild.colors = new_colors
        guild.reindex()


    def rand_color(self):
        """Returns a random color object"""
        try:
            return random.choice(self.colors)
        except IndexError:
            return None


    @classmethod
    def from_json(cls, theme):
        """Creates a Theme object from valid JSON"""
        new_theme = cls(theme["name"], theme["guild_id"],
                        theme["description"])
        for color in theme["colors"]:
            new_theme.colors.append(Color.from_json(color))
        return new_theme
