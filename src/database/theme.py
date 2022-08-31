import model

from database import errors

from .guild import db, insert_guild

theme_cache: dict[int, list[model.Theme]] = {}


def get_themes(id: int, from_cache=True) -> list[model.Theme]:
    """Fetch all the themes a guild has."""
    # check for colors in cache
    if id in theme_cache and from_cache:
        return theme_cache[id]

    # find guild or use default if not found
    data = db.Guilds.find_one({"_id": id}, {"_id": False, "themes": True}) or insert_guild(id=id)

    # update cache
    themes = [model.Theme.from_dict(theme) for theme in data["themes"]]
    theme_cache[id] = themes

    return themes


def add_theme(id: int, theme: model.Theme) -> None:
    """Push a theme to the theme list."""
    response = db.Guilds.update_one(
        filter={"_id": id},
        update={"$push": {"themes": theme.as_dict()}}
    )

    if response.modified_count == 0:
        raise errors.DatabaseError("Couldn't Add Theme")

    # update cache
    if id in theme_cache:
        theme_cache[id].append(theme)


def remove_theme(id: int, theme: model.Theme) -> None:
    """Remove a theme from the list of themes."""
    response = db.Guilds.update_one(
        filter={"_id": id},
        update={"$pull": {"themes": theme.as_dict()}}
    )

    if response.modified_count == 0:
        raise errors.DatabaseError("Couldn't Remove Theme")

    # update cache
    if id in theme_cache:
        theme_cache[id].remove(theme)


def update_theme(id: int, old: model.Theme, new: model.Theme) -> None:
    """Update a color be it the name/value/role."""
    response = db.Guilds.update_one(
        {"_id": id, "themes": old.as_dict()},
        {"$set": {"themes.$": new.as_dict()}}
    )

    if response.modified_count == 0:
        raise errors.DatabaseError("Couldn't Update Theme")

    # Update Cache
    if id in theme_cache:
        for i, theme in enumerate(theme_cache[id]):
            if theme == old:
                theme[id][i] = new
