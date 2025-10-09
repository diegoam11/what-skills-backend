from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.user import UserCreate, UserResponse, EmployabilityData, EmployabilityScore, Recommendation
from utils.auth import get_password_hash
from datetime import datetime
from bson import ObjectId


class UserRepository:
    """Repository for user data operations"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.users_collection = database.users
        self.employability_collection = database.employability_data
        self.scores_collection = database.employability_scores
        self.recommendations_collection = database.recommendations
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        user_dict = {
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "email": user_data.email,
            "password": hashed_password,
            "career": user_data.career,
            "university": user_data.university,
            "semester": user_data.semester,
            "created_at": datetime.utcnow()
        }
        
        result = await self.users_collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        
        return UserResponse(**user_dict)
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email (returns raw dict for authentication)"""
        return await self.users_collection.find_one({"email": email})
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID"""
        user_dict = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        if user_dict:
            return UserResponse(**user_dict)
        return None
    
    async def get_all_users(self) -> List[UserResponse]:
        """Get all users"""
        cursor = self.users_collection.find({})
        users = []
        async for user_dict in cursor:
            users.append(UserResponse(**user_dict))
        return users
    
    # Employability Data Operations
    async def save_employability_data(self, data: EmployabilityData) -> bool:
        """Save or update employability data"""
        data_dict = data.dict(by_alias=True)
        result = await self.employability_collection.replace_one(
            {"_id": data.user_id},
            data_dict,
            upsert=True
        )
        return result.acknowledged
    
    async def get_employability_data(self, user_id: str) -> Optional[EmployabilityData]:
        """Get employability data for user"""
        data_dict = await self.employability_collection.find_one({"_id": ObjectId(user_id)})
        if data_dict:
            return EmployabilityData(**data_dict)
        return None
    
    # Employability Score Operations
    async def save_employability_score(self, score: EmployabilityScore) -> bool:
        """Save employability score"""
        score_dict = score.dict(by_alias=True)
        result = await self.scores_collection.insert_one(score_dict)
        return result.acknowledged
    
    async def get_latest_employability_score(self, user_id: str) -> Optional[EmployabilityScore]:
        """Get latest employability score for user"""
        score_dict = await self.scores_collection.find_one(
            {"user_id": ObjectId(user_id)},
            sort=[("calculated_at", -1)]
        )
        if score_dict:
            return EmployabilityScore(**score_dict)
        return None
    
    async def get_employability_history(self, user_id: str, limit: int = 10) -> List[EmployabilityScore]:
        """Get employability score history"""
        cursor = self.scores_collection.find(
            {"user_id": ObjectId(user_id)}
        ).sort("calculated_at", -1).limit(limit)
        
        scores = []
        async for score_dict in cursor:
            scores.append(EmployabilityScore(**score_dict))
        return scores
    
    # Recommendations Operations
    async def save_recommendations(self, recommendations: List[Recommendation]) -> bool:
        """Save recommendations for a user"""
        if not recommendations:
            return True
        
        # Delete old recommendations for the user
        user_id = recommendations[0].user_id
        await self.recommendations_collection.delete_many({"user_id": user_id})
        
        # Insert new recommendations
        recommendations_dict = [rec.dict(by_alias=True) for rec in recommendations]
        result = await self.recommendations_collection.insert_many(recommendations_dict)
        return result.acknowledged
    
    async def get_recommendations(self, user_id: str, limit: int = 10) -> List[Recommendation]:
        """Get recommendations for user"""
        cursor = self.recommendations_collection.find(
            {"user_id": ObjectId(user_id)}
        ).sort("priority", 1).limit(limit)
        
        recommendations = []
        async for rec_dict in cursor:
            recommendations.append(Recommendation(**rec_dict))
        return recommendations
