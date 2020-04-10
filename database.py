import os
import sys
from pymongo import MongoClient
from classes import Guild
from vars import bot

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
        Guild.from_json(guild_dict)  # build guild


def clear_abandoned_guilds():
    """Remove guilds that the bot cannot see"""
    guilds = {guild.id for guild in bot.guilds}
    db_guilds = {guild.id for guild in Guild._guilds.values()}

    abandoned = db_guilds - guilds
    for id in abandoned:
        print(f"Removed {id} from database")
        Guild._guilds.pop(id)  # remove from internal list
        coll.delete_one({"id": id})  # remove from MongoD
