"""This module houses all file drawing functions."""

import io
import math
from typing import TYPE_CHECKING

import discord
from PIL import Image, ImageDraw, ImageFont

from .utils import chunk

if TYPE_CHECKING:
    from model import Color, Theme


def roboto(size: int):
    return ImageFont.truetype("./src/resources/fonts/Roboto.ttf", size=size)


def convert_to_discord_file(image: Image.Image, name: str | None = None):
    """Convert PIL.Image to discord.File"""
    byte_arr = io.BytesIO()
    image.save(byte_arr, format='PNG')
    byte_arr = byte_arr.getvalue()
    im = io.BytesIO(byte_arr)
    return discord.File(im, filename=name or "colors.png")


def draw_colors(
    colors: list["Color"],
    columns: int = 3,
    row_height: int = 50,
    column_width: int = 300
) -> discord.File:
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
    font = roboto(30)

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

        draw.rounded_rectangle(
            xy=(upper_left, lower_right),
            radius=10,
            fill=color.rgb,
            outline=(0, 0, 0, 0),
            width=3
        )

        text = f"{color.name}"
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


def draw_themes(themes: list["Theme"], row_height: int = 120, chunksize: int = 5) -> list[discord.File]:
    """Creates an image displaying themes."""
    canvas_width = 900

    theme_chunks = chunk(themes, chunksize=chunksize)

    text_top = int(row_height * .10)  # text is drawn at 10% of container height
    text_height = int(row_height * .30)  # text is 30% of container

    color_top = int(row_height * .50)  # color is drawn at 50% of container height
    color_height = int(row_height * .45)  # color is 40% of container

    fnt = roboto(size=text_height)

    theme_images = []
    for i, theme_chunk in enumerate(theme_chunks):
        # Create new blank image
        img = Image.new(
            mode='RGBA',
            size=(canvas_width, row_height * len(theme_chunk)),
            color=(0, 0, 0, 0)
        )
        draw = ImageDraw.Draw(img)  # set image for drawing

        # Draw each theme
        for j, theme in enumerate(theme_chunk):
            text = f"{theme.name}"

            # text coords (x, y) indicates top left corner of text
            text_width, text_height = draw.textsize(text, fnt)
            x = (canvas_width/2)-(text_width/2)  # centered text
            y = j * row_height + text_top
            draw.text((x, y), text, font=fnt, fill=(240, 240, 240))

            color_width = canvas_width/len(theme.colors)

            # Draw each color
            for k, color in enumerate(theme.colors):
                # top left corner
                x0 = k * color_width
                y0 = j * row_height + color_top
                # bottom right corner
                x1 = x0 + color_width - 5  # 5 is color spacing
                y1 = y0 + color_height

                draw.rounded_rectangle(
                    xy=(x0, y0, x1, y1),
                    radius=10,
                    fill=color.rgb
                )

        theme_images.append(img)
    return [convert_to_discord_file(img, f"themes{i}.png") for i, img in enumerate(theme_images)]
