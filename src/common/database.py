import os

import pymongo
from model.color import Color

# database connection setup
mongo_string = f"mongodb+srv://Gumbachi:{os.getenv('MONGO_PASS')}@discordbotcluster.afgyl.mongodb.net/VibrantDB?retryWrites=true&w=majority"
connection = pymongo.MongoClient(mongo_string)

print("Connected to Database.")


class DB:
    def __init__(self, connection: pymongo.MongoClient):
        self._db = connection.VibrantDB
        print("Connected to DB")

    @staticmethod
    def default_guild(id: int):
        return {"_id": id, "welcome_channel": None, "colors": [], "themes": []}

    def insert_guild(self, id: int):
        """Insert a guild for the id provided and return the empty guild"""
        empty_guild = self.default_guild(id=id)
        self._db.Guilds.insert_one(empty_guild)
        return empty_guild

    def get_guild(self, id: int) -> dict:
        """Fetch the guild document or add one if not exists."""
        data = self._db.Guilds.find_one({"_id": id})
        return data if data != None else self.insert_guild(id=id)

    def get_colors(self, id: int) -> list[Color]:
        """Fetch colors for a guild and add guilds if not exists"""
        data = self._db.Guilds.find_one(
            {"_id": id}, {"_id": False, "colors": True})

        if data == None:
            data = self.insert_guild(id=id)

        return [Color.from_dict(color) for color in data["colors"]]

    def add_color(self, id: int, color: Color) -> bool:
        """Push a color to the color list and report success"""
        response = self._db.Guilds.update_one(
            filter={"_id": id},
            update={"$push": {"colors": color.__dict__}}
        )

        return response.modified_count != 0

    def remove_color(self, id: int, color: Color) -> bool:
        """Remove a color from the color list and report success"""
        response = self._db.Guilds.update_one(
            filter={"_id": id},
            update={"$pull": {"colors": color.__dict__}}
        )

        return response.modified_count != 0


db = DB(connection)


# def get(gid, field):
#     """Fetches and unpacks one field from the database."""
#     try:
#         data = guilds.find_one({"_id": gid}, {field: 1, "_id": 0})
#         return data[field]
#     except TypeError:
#         data = {
#             "_id": gid,
#             "prefix": "$",
#             "wc": None,
#             "colors": [],
#             "themes": []
#         }
#         guilds.insert_one(data)
#         return data[field]


# def get_many(gid, *fields):
#     """Fetches and unpacks many field from the database."""
#     # Query document
#     try:
#         projection = {field: 1 for field in fields}
#         projection.update({"_id": 0})  # ignore id field
#         data = guilds.find_one({"_id": gid}, projection)
#         return data.values()

#     # Fix empty document
#     except TypeError:
#         data = {
#             "_id": gid,
#             "prefix": "$",
#             "wc": None,
#             "colors": [],
#             "themes": []
#         }
#         guilds.insert_one(data)
#         return [data[f] for f in fields]
