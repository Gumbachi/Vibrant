import os

import pymongo

import src.database.errors as errors

# database connection setup
mongo_string = f"mongodb+srv://Gumbachi:{os.getenv('MONGO_PASS')}@discordbotcluster.afgyl.mongodb.net/VibrantDB?retryWrites=true&w=majority"
connection = pymongo.MongoClient(mongo_string)
db = connection["VibrantDB"]
guilds = db["Guilds"]

print("Connected to DB")


def generate_default_guild(guild_id: int):
    return {"_id": guild_id, "colors": [], "themes": []}


def insert_guild(guild_id: int):
    """Insert a guild for the id provided and return the empty guild."""
    empty_guild = generate_default_guild(guild_id=guild_id)
    result = guilds.insert_one(document=empty_guild)

    if result.acknowledged:
        return empty_guild
    else:
        raise errors.DatabaseError("Database write was not acknowledged")




def delete_guild(id: int):
    """Delete a guild from the database."""
    # Remove from cache
    from .color import color_cache
    from .theme import theme_cache
    color_cache.pop(id, None)
    theme_cache.pop(id, None)

    db.Guilds.delete_one({"_id": id})


def get_guild(guild_id: int) -> dict:
    """Fetch the guild document or add one if not exists."""
    data = guilds.find_one({"_id": guild_id})

    # return found data or a default guild
    return data if data is not None else insert_guild(guild_id=guild_id)
