import copy
import io
import json
import math
import os
import re
import random

import numpy as np
import scipy
import scipy.cluster
import binascii
import discord
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps
from fuzzywuzzy import process

import classes as c
from cfg import coll  # collection from mongoDB
from vars import preset_names, heavy_command_active


def update_prefs(*guilds):
    """
    Update the linked mongoDB database. Updates all if arg is left blank.

    Args:
        guilds (list of Guild): list of guild to update
    """

    print("UPDATING")
    for guild in guilds:
        json_data = guild.to_json()  # serialize objects

        # find a document based on ID and update update
        if coll.find_one({"id": guild.id}):
            if not coll.find_one(json_data):
                coll.find_one_and_update({"id": guild.id}, {'$set': json_data})
        else:
            # add new document if guild is not found
            coll.insert_one(json_data)


def get_prefs():
    """Generates objects from json format to python objects from mongoDB

    Only runs on start of program
    """
    c.Guild._guilds.clear()  # remove all guilds to be remade
    data = list(coll.find())  # get mongo data
    if not data:
        return

    for guild_dict in data:
        guild = c.Guild.from_json(guild_dict)  # build guild
        guild.reset_ids()


def check_hex(string):
    """Verify if a string is a valid hexcode."""
    return bool(re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', string))


def is_disabled(channel):
    """Evaluate if a discord channel is disabled."""
    return (isinstance(channel, discord.DMChannel)
            or channel.id in c.Guild.get(channel.guild.id).disabled_channel_ids)


def draw_presets():
    """Draws a preset based on colorbot presets

    Returns:
        A byte array of the image
    """
    row_height = 60
    canvas_width = 900
    text_width = 250

    img = Image.new('RGB', (canvas_width, len(preset_names) * row_height),
                    color=(54, 57, 63))  # generate image
    draw = ImageDraw.Draw(img)  # set image for drawing
    fnt = ImageFont.truetype(
        f'.{os.path.sep}assets{os.path.sep}OpenSans-Regular.ttf', 40)  # set font
    text_color = (255, 255, 255)  # white text
    margin = 5

    # draws boxes based on amount of items and colors each box and labels them
    for i, preset in enumerate(preset_names):
        with open(f"presets{os.path.sep}{preset}.json") as data_file:
            set_data = json.load(data_file)

        # draw text on rectangles
        draw.text((20, i*row_height), f"{preset}: ", font=fnt, fill=text_color)
        w, _ = draw.textsize(f"{preset}: ", fnt)
        w += 20  # include margin

        amt_colors = len(set_data)
        rem_space = canvas_width - text_width - margin
        width_of_rect = rem_space/amt_colors

        for j, color in enumerate(set_data, 0):
            rgb = hex_to_rgb(color['hexcode'])
            x1 = j * width_of_rect + text_width + margin  # +5 for segmentation margin
            x2 = i * row_height + margin
            y1 = (j+1) * width_of_rect + text_width
            y2 = (i+1) * row_height - margin
            draw.rectangle([x1, x2, y1, y2], fill=rgb)

    # return binary data
    imgByteArr = io.BytesIO()
    img.save(imgByteArr, format='PNG')
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr


def rgb_to_hex(rgb):
    """Convert rgb tuple to hexcode string."""
    return "#%02x%02x%02x" % rgb


def hex_to_rgb(value):
    """Convert hexcode string to rgb tuple."""
    value = value.lstrip('#')
    if len(value) == 3:
        value = u''.join(2 * s for s in value)
    lv = len(value)
    return tuple(int(value[i:i+lv//3], 16) for i in range(0, lv, lv//3))
