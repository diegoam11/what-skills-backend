from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = Database()

async def get_database():
    return db.database

async def connect_to_mongo():
    """Create database connection"""
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017/whatskills")
    db.client = AsyncIOMotorClient(mongo_url)
    db.database = db.client.whatskills
    
    # Test connection
    try:
        await db.client.admin.command('ping')
        print("✅ Connected to MongoDB")
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")

    def get_collection(self, db_name: str, collection_name: str):
        return self.client[db_name][collection_name]

    def close(self):
        self.client.close()


@lru_cache()
def get_mongo_connection() -> MongoConnection:
    print("[MONGODB] Establishing connection...")
    return MongoConnection()
