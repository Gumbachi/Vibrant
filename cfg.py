import os
import sys
from pymongo import MongoClient

# database setup
client = MongoClient(f"mongodb+srv://Gumbachi:{os.environ['MONGO_PASS']}@cluster0-wglq9.mongodb.net/test?retryWrites=true&w=majority")
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
