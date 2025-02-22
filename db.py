from pymongo import MongoClient

# Connect to MongoDB (Replace <your_connection_string> with MongoDB URI)
client = MongoClient("<your_connection_string>")
db = client["CatalystBankingIAM"]

# Collections
logins_collection = db["logins"]
file_access_collection = db["file_access"]
