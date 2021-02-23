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

# def add_guild(id):
#     """Adds a blank guild"""
#     update_guild(id, blank_guild)
#     return blank_guild


# def get(id, *fields):
#     """Fetch data in a specific field using a projection and update fields if it doesnt exist."""

#     # Fetch data
#     projection = {field: 1 for field in fields}
#     projection.update({"_id": 0})
#     data = guildcoll.find_one({"_id": id}, projection)

#     # if doc doesnt exist add blank doc
#     if not data:
#         data = add_guild(id)  # add guild to db and update data

#     output = []  # return data for each field given
#     for field in fields:
#         try:
#             output.append(data[field])

#         # return default field value if field doesnt exist in document and add field
#         except KeyError:
#             update_guild(id, {field: blank_guild[field]})
#             output.append(blank_guild[field])

#     # return 1 variable or a list depending on size for unpacking reasons
#     return output[0] if len(output) == 1 else output


# def update_member(id, data):
#     usercoll.update_one({"_id": id}, {"$set": data}, upsert=True)


# def find_member(id):
#     """Find member document for easy role lookup"""
#     member = usercoll.find_one({"_id": id})
#     if member:
#         return member
#     else:
#         usercoll.insert_one({"_id": id})
#         return {}
