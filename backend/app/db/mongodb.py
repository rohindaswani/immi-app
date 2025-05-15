from pymongo import MongoClient
from pymongo.database import Database

from app.core.config import settings

# MongoDB client
client = None
db = None

# This will be initialized when the MongoDB URL is available
if settings.MONGODB_URL:
    client = MongoClient(settings.MONGODB_URL)
    db_name = settings.MONGODB_URL.split("/")[-1]
    db = client[db_name]


def get_mongo_db() -> Database:
    """
    Get the MongoDB database instance.
    """
    if not db:
        raise Exception("MongoDB connection not initialized")
    
    return db


def get_collection(collection_name: str):
    """
    Get a MongoDB collection.
    """
    database = get_mongo_db()
    return database[collection_name]