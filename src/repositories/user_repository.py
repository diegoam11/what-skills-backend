from bson import ObjectId

from config.db import get_mongo_connection
from models.user import UserResponse


class UserRepository:
    def __init__(self):
        mongo_conn = get_mongo_connection()
        self.users = mongo_conn.get_collection("test", "users")

    def find_users(self, projection: list[str] = None) -> list[UserResponse]:
        projection_dict = {field: 1 for field in projection} if projection else None
        users_db = list(self.users.find({}, projection_dict))

        for u in users_db:
            if "_id" in u and isinstance(u["_id"], ObjectId):
                u["_id"] = str(u["_id"])

        return [UserResponse(**u) for u in users_db]
