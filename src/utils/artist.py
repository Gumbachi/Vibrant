"""This module houses all file drawing functions."""

import math
import io

from PIL import Image, ImageDraw, ImageFont
import discord

from model.color import Color


def convert_to_discord_file(image: Image):
    """Convert PIL.Image to discord.File"""
    byte_arr = io.BytesIO()
    image.save(byte_arr, format='PNG')
    byte_arr = byte_arr.getvalue()
    im = io.BytesIO(byte_arr)
    return discord.File(im, filename="colors.png")


def draw_colors(colors: list[Color], columns: int = 3, row_height: int = 50, column_width: int = 300):
    """Draws an image for discord representing a list of colors."""

    rows = math.ceil(len(colors) / columns)  # amt of rows needed

    image_width = columns * column_width
    image_height = rows * row_height

    image = Image.new(
        mode='RGBA',
        size=(image_width, image_height),
        color=(0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(image)  # set image for drawing
    font = ImageFont.truetype(f"./src/resources/fonts/Roboto.ttf", size=30)

    # draws and labels boxes
    for i, color in enumerate(colors):

        # draw boxes
        current_column = i % columns  # 0,1,2 repeating if columns=3
        current_row = i // columns  # increment every 3 elements if columns=3

        # determine rectange corner positions
        upper_left = (
            column_width * current_column,  # Upper left corner X coordinate
            row_height * current_row  # Upper left corner Y coordinate
        )
        lower_right = (
            upper_left[0] + column_width,  # Lower right corner X coordinate
            upper_left[1] + row_height  # Lower right corner Y coordinate
        )

        draw.rectangle(
            xy=(upper_left, lower_right),
            fill=color.rgb,
            outline=(0, 0, 0, 0),
            width=2
        )

        text = f"{i + 1}. {color.name}"
        text_width, _ = draw.textsize(text, font)

        # Ellipsize text
        text_size_limit = column_width - (column_width/10)
        while text_width > text_size_limit:
            text = text[:-2]  # Cut off two characters
            text_width, _ = draw.textsize(text, font)
            if text_width <= text_size_limit:
                text += "..."

        # Draw text on boxes
        x = upper_left[0] + (column_width-text_width)/2
        y = upper_left[1] + 10
        draw.text(
            xy=(x, y),
            text=text,
            font=font,
            fill=color.optimal_text_color
        )

    return convert_to_discord_file(image)
