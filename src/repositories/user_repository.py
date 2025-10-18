from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..models.user import UserCreate, UserResponse, EmployabilityData, EmployabilityScore, Recommendation
from ..utils.auth import get_password_hash
from datetime import datetime
from bson import ObjectId

from src.config.db import get_mongo_connection
from src.models.user import UserCreate, UserResponse


class UserRepository:
    def __init__(self):
        mongo_conn = get_mongo_connection()
        self.users = mongo_conn.get_collection("what-skills-db", "users")

    def find_users(self, projection: list[str] = None) -> list[UserResponse]:
        projection_dict = {field: 1 for field in projection} if projection else None
        users_db = list(self.users.find({}, projection_dict))

        for u in users_db:
            if "_id" in u and isinstance(u["_id"], ObjectId):
                u["_id"] = str(u["_id"])

        return [UserResponse(**u) for u in users_db]

    def create_user(self, user: UserCreate) -> UserResponse:
        result = self.users.insert_one(user.model_dump())
        created_user = self.users.find_one({"_id": result.inserted_id})

        if (
            created_user
            and "_id" in created_user
            and isinstance(created_user["_id"], ObjectId)
        ):
            created_user["_id"] = str(created_user["_id"])

        return UserResponse(**created_user)
