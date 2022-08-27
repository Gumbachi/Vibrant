import model

from database import errors

from .guild import db, insert_guild

# top level cache for minimizing database calls
color_cache: dict[int, list[model.Color]] = {}


def get_colors(id: int, from_cache=True) -> list[model.Color]:
    """Fetch colors for a guild and add guilds if not exists"""

    # check for colors in cache
    if id in color_cache and from_cache:
        print("Colors from CACHE")
        return color_cache[id]

    print("Colors from ATLAS")

    # find guild or use default if not found
    data = db.Guilds.find_one({"_id": id}, {"_id": False, "colors": True}) or insert_guild(id=id)

    # update cache
    colors = [model.Color.from_dict(color) for color in data["colors"]]
    color_cache[id] = colors

    return colors


def add_color(id: int, color: model.Color) -> None:
    """Push a color to the color list."""
    response = db.Guilds.update_one(
        filter={"_id": id},
        update={"$push": {"colors": color.as_dict()}}
    )

    if response.modified_count == 0:
        raise errors.DatabaseError("Couldn't Add Color")

    # update cache
    if id in color_cache:
        color_cache[id].append(color)


def remove_color(id: int, color: model.Color) -> None:
    """Remove a color from the color list."""
    response = db.Guilds.update_one(
        filter={"_id": id},
        update={"$pull": {"colors": color.as_dict()}}
    )

    if response.modified_count == 0:
        raise errors.DatabaseError("Couldn't Remove Color")

    # update cache
    if id in color_cache:
        color_cache[id].remove(color)


def update_color(id: int, old: model.Color, new: model.Color) -> None:
    """Update a color in the database."""
    response = db.Guilds.update_one(
        {"_id": id, "colors": old.as_dict()},
        {"$set": {"colors.$": new.as_dict()}}
    )

    if response.modified_count == 0:
        raise errors.DatabaseError(f"Couldn't Update Color\n{old}, {new}")

    # Update Cache
    if id in color_cache:
        for i, color in enumerate(color_cache[id]):
            if color == old:
                color_cache[id][i] = new


def replace_colors(id: int, colors: list[model.Color]):
    """Replace all colors with a new list of colors."""
    response = db.Guilds.update_one(
        filter={"_id": id},
        update={"$set": {"colors": [c.as_dict() for c in colors]}}
    )

    if response.modified_count == 0:
        raise errors.DatabaseError("Couldn't Update Colors")

    # update cache
    if id in color_cache:
        color_cache[id] = colors
