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
from vars import preset_names


async def update_prefs(guilds=None):
    """Updates the linked mongoDB database. Updates all if arg is left blank

    Args:\n
        guilds (list of Guild): list of guild to update
    """
    if not guilds:
        guilds = list(c.Guild._guilds.values())

    for guild in guilds:
        json_data = serialize(guild) # serialize objects

        # find a document based on ID and update update
        if coll.find_one({"id": guild.id}):
            if not coll.find_one(json_data):
                coll.find_one_and_update({"id": guild.id}, {'$set': json_data})
        else:
            # add new document if guild is not found
            coll.insert_one(json_data)


async def get_prefs():
    """Generates objects from json format to python objects from mongoDB

    Only runs on start of program
    """
    c.Guild._guilds.clear()  # remove all guilds to be remade
    data = list(coll.find())  # get mongo data
    if not data:
        return

    for dictionary in data:
        c.Guild.from_json(dictionary)  # builds guild objects from dictionaries


def check_hex(search):
    """Verify that a string is a valid hexcode

    Args:\n
        search (string): The string to be validated

    Returns:\n
        bool: if search was valid hex or not
    """
    valid = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', search)
    return True if valid else False


def is_disabled(channel):
    """Evaluates if a channel is disabled

    Args:\n
        channel (discord.channel): The channel to get info from

    Returns:\n
        bool: if the channel is enabled
    """
    if isinstance(channel, discord.DMChannel):
        return True
    if channel.id in c.Guild.get_guild(channel.guild.id).disabled_channels:
        return True
    else:
        return False


def serialize(obj):
    """Convert an object into valid json

    Args:\n
        obj (Snowflake): The object you want to be serialized

    Returns:\n
        dict: The dictionary of the object
    """
    # dic = copy.deepcopy(guild).__dict__
    # dic["colors"] = [color.__dict__ for color in dic["colors"]]
    # return dic

    data = json.loads(json.dumps(obj, default=lambda o: o.__dict__))
    return data


def find_user(message, query, guild, threshold=80):
    """Searches for a user in the guild with a query

    Args:
        message (discord.Message): the message with command
        query (str): the name to search for
        guild (discord.Guild): the guild the member is in
        threshold (int): the fuzzy matching threshold

    Returns:
        discord.User: the user if found
    """
    if message.mentions:
        user = message.mentions[0]
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


def pfp_analysis(URL):
    NUM_CLUSTERS = 5
    response = requests.get(URL)
    im = Image.open(io.BytesIO(response.content))
    im = im.resize((150, 150))      # optional, to reduce time
    ar = np.asarray(im)
    shape = ar.shape
    ar = ar.reshape(np.product(shape[:2]), shape[2]).astype(float)

    #print('finding clusters')
    codes, _ = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
    #print('cluster centres:\n', codes)

    vecs, _ = scipy.cluster.vq.vq(ar, codes)         # assign codes
    counts, _ = np.histogram(vecs, len(codes))    # count occurrences

    index_max = np.argmax(counts)                    # find most frequent
    rgb = codes[index_max]
    hexcode = binascii.hexlify(bytearray(int(c) for c in rgb)).decode('ascii')
    #print(f'most frequent is {rgb} ({hexcode})')
    return f"#{hexcode[:6]}"


def rgb_to_hex(rgb):
    """Converts rgb tuple to hexcode string"""
    return '%02x%02x%02x' % rgb


def hex_to_rgb(value):
    """Converts hexcode string to rgb tuple"""
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i+lv//3], 16) for i in range(0, lv, lv//3))
