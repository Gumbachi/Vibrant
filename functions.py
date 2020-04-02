import os
import json
import re
import io

import discord
from PIL import Image, ImageDraw, ImageFont

from vars import heavy_command_active


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
