from pymongo import MongoClient

def get_mongo_client():
    mongo_user = "admin"
    mongo_pass = "password123"
    client = MongoClient(f"mongodb://{mongo_user}:{mongo_pass}@localhost:27017/")
    db = client["talentum_db"]
    return db