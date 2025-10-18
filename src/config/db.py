import os
from functools import lru_cache

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")


class MongoConnection:
    def __init__(self, connection_string=MONGODB_URI):
        self.client = MongoClient(connection_string)

    def get_database(self, db_name: str):
        return self.client[db_name]

    def get_collection(self, db_name: str, collection_name: str):
        return self.client[db_name][collection_name]

    def close(self):
        self.client.close()


@lru_cache()
def get_mongo_connection() -> MongoConnection:
    print("[MONGODB] Establishing connection...")
    return MongoConnection()
