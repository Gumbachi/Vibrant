import os
from pymongo import MongoClient

# database setup
client = MongoClient(os.environ['MONGO_KEY'])

if os.environ["BOT_VERSION"] == "real":
	print("Using Real Collection")
	db = client.colorbot_db
	coll = db.data
elif os.environ["BOT_VERSION"] == "test":
	print("Using Test Collection")
	db = client.colorbot_db
	coll = db.ColorTest
