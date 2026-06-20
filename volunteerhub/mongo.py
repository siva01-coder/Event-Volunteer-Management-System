from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["volunteerhub_db"]

events_collection = db["events"]
users_collection = db["users"]
registrations_collection = db["registrations"]
tasks_collection = db["tasks"]
