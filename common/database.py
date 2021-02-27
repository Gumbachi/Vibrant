import os
import pymongo

# database connection setup
mongo_string = f"mongodb+srv://Gumbachi:{os.getenv('MONGO_PASS')}@discordbotcluster.afgyl.mongodb.net/VibrantDB?retryWrites=true&w=majority"
db = pymongo.MongoClient(mongo_string).VibrantDB

guilds = db.Guilds

print("Connected to Database.")


def get(gid, field):
    """Fetches and unpacks one field from the database."""
    data = guilds.find_one({"_id": gid}, {field: 1, "_id": 0})
    if not data:
        data = {
            "_id": gid,
            "prefix": "$",
            "wc": None,
            "colors": [],
            "themes": []
        }
        guilds.insert_one(data)
    return data[field]


def get_many(gid, *fields):
    """Fetches and unpacks many field from the database."""
    projection = {field: 1 for field in fields}
    projection.update({"_id": 0})

    data = guilds.find_one({"_id": gid}, projection)
    if not data:
        data = {
            "_id": gid,
            "prefix": "$",
            "wc": None,
            "colors": [],
            "themes": []
        }
        guilds.insert_one(data)
    return data.values()
