import os
import sys
from pymongo import MongoClient
from classes import Guild

# database setup
client = MongoClient(
    f"mongodb+srv://Gumbachi:{os.environ['MONGO_PASS']}@cluster0-wglq9.mongodb.net/test?retryWrites=true&w=majority")
db = client.VibrantDB

# Choose collection in database
if os.environ["BOT_VERSION"] == "real":
    print("Using Real Collection")
    coll = db.VibrantData
elif os.environ["BOT_VERSION"] == "test":
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


def get_prefs():
    """Generates objects from json format to python objects from mongoDB

    Only runs on start of program
    """
    Guild._guilds.clear()  # remove all guilds to be remade
    data = list(coll.find())  # get mongo data

    for guild_dict in data:
        guild = Guild.from_json(guild_dict)  # build guild
        guild.reset_ids()
