import os
import sys
from pymongo import MongoClient
from classes import Guild
from vars import bot

# database setup
client = MongoClient(
    f"mongodb+srv://Gumbachi:{os.getenv('MONGO_PASS')}@cluster0-wglq9.mongodb.net/test?retryWrites=true&w=majority")
db = client.VibrantDB

version = os.getenv("BOT_VERSION")
# Choose collection in database
if version == "real":
    print("Using Real Collection")
    coll = db.VibrantData
elif version == "test":
    print("Using Test Collection")
    coll = db.VibrantTestData
else:
    print("Couldn't connect to MongoDB. Exiting Program")
    sys.exit()


def update_prefs(*guilds):
    """
    Update the linked mongoDB database. Updates all if arg is left blank.

    Args:
        guilds (list of Guild): list of guild to update
    """
    for guild in guilds:
        json_data = guild.to_json()  # serialize objects

        # find a document based on ID and update update
        if coll.find_one({"id": guild.id}):
            if not coll.find_one(json_data):
                coll.find_one_and_update({"id": guild.id}, {"$set": json_data})
        else:
            # add new document if guild is not found
            coll.insert_one(json_data)


def find_guild(id):
    """Find the guild by id in the database"""
    return coll.find_one({"id": id})


def delete_guild(id):
    """Find the guild by id in the database and delete"""
    return coll.delete_one({"id": id})
