import os

import pymongo

# database connection setup
mongo_string = f"mongodb+srv://Gumbachi:{os.getenv('MONGO_PASS')}@discordbotcluster.afgyl.mongodb.net/VibrantDB?retryWrites=true&w=majority"
connection = pymongo.MongoClient(mongo_string)
db = connection.VibrantDB

print("Connected to DB")


def generate_default_guild(id: int):
    return {"_id": id, "colors": [], "themes": []}


def insert_guild(id: int):
    """Insert a guild for the id provided and return the empty guild."""
    empty_guild = generate_default_guild(id=id)
    db.Guilds.insert_one(empty_guild)
    return empty_guild


def delete_guild(id: int):
    """Delete a guild from the database."""
    # Remove from cache
    from .color import color_cache
    from .theme import theme_cache
    color_cache.pop(id, None)
    theme_cache.pop(id, None)

    db.Guilds.delete_one({"_id": id})


def get_guild(id: int) -> dict:
    """Fetch the guild document or add one if not exists."""
    data = db.Guilds.find_one({"_id": id})

    # return found data or a default guild
    return data if data is not None else insert_guild(id=id)
