"""Contains utility functions for the bot"""

import re
import io
import os
from os.path import sep
import json
import math

import discord
from PIL import Image, ImageDraw, ImageFont


def check_hex(string):
    """Verify if a string is a valid hexcode."""
    return bool(re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', string))


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


def to_sendable(image, name="image"):
    # Convert PIL Image to discord File
    im = image.copy()
    byte_arr = io.BytesIO()
    im.save(byte_arr, format='PNG')
    byte_arr = byte_arr.getvalue()
    im = io.BytesIO(byte_arr)
    return discord.File(im, filename=f"{name}.png")


def draw_imports():
    color_height = 44  # height of color boxes
    cont_height = 112 + 7  # container height
    canvas_width = 900
    padding_above_text = 20
    padding_below_text = 10
    box_margin = 5

    # set font
    fnt = ImageFont.truetype(
        f"assets{os.path.sep}Roboto.ttf",
        size=40)

    presets = os.listdir(f"presets{sep}")

    images = []

    for x in range(math.ceil(len(presets)/5)):
        # x is 1, 2, 3

        start = x * 5
        end = len(presets) if start + 5 > len(presets) else start + 5

        cut_presets = presets[start:end]
        rows = len(cut_presets)

        img = Image.new(mode='RGBA',
                        size=(canvas_width, cont_height * rows),
                        color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)  # set image for drawing

        # draws themes
        for i, filename in enumerate(cut_presets):
            with open(f"presets{sep}{filename}", "r") as f:
                preset = json.load(f)

            # draw text
            msg = f"{preset['name']}: {preset['description']}"
            text_width, text_height = draw.textsize(msg, fnt)

            # text coords
            x = (canvas_width/2)-(text_width/2)  # center
            y = i * cont_height + padding_above_text

            text_height += padding_above_text + padding_below_text

            draw.text((x, y), msg, font=fnt, fill=(255, 255, 255))

            width_of_rect = canvas_width/len(preset["colors"])

            # draw color preview
            for j, color in enumerate(preset["colors"], 0):
                # top left corner
                x0 = j * width_of_rect
                y0 = i * cont_height + text_height

                # bottom right corner
                x1 = x0 + width_of_rect - box_margin
                y1 = y0 + color_height

                value = hex_to_rgb(color["hexcode"])
                draw.rectangle([(x0, y0), (x1, y1)], fill=value)

        images.append(img)
    return images
