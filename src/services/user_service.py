from typing import Optional, List
from fastapi import HTTPException, status
from ..models.user import (
    UserCreate, UserLogin, UserResponse, Token, 
    EmployabilityData, EmployabilityScore, Recommendation
)
from ..repositories.user_repository import UserRepository
from .employability_service import EmployabilityCalculator, generate_sample_employability_data
from .recommendation_service import RecommendationService
from ..utils.auth import verify_password, create_access_token, get_password_hash
from datetime import timedelta


class UserService:
    """Service layer for user operations"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.employability_calculator = EmployabilityCalculator()
        self.recommendation_service = RecommendationService()
    
    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """Register a new user"""
        # Check if user already exists
        existing_user = await self.user_repository.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = await self.user_repository.create_user(user_data)
        
        # Generate sample employability data for new user
        sample_data = generate_sample_employability_data(user.id)
        await self.user_repository.save_employability_data(sample_data)
        
        # Calculate initial employability score
        score = self.employability_calculator.calculate_score(sample_data)
        await self.user_repository.save_employability_score(score)
        
        # Generate initial recommendations
        recommendations = self.recommendation_service.generate_recommendations(
            user.id, sample_data, score
        )
        await self.user_repository.save_recommendations(recommendations)
        
        return user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        """Authenticate user credentials"""
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user["password"]):
            return None
        
        return user
    
    async def login_user(self, login_data: UserLogin) -> Token:
        """Login user and return access token"""
        user = await self.authenticate_user(login_data.email, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user["email"]}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email"""
        user_dict = await self.user_repository.get_user_by_email(email)
        if user_dict:
            return UserResponse(**user_dict)
        return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID"""
        return await self.user_repository.get_user_by_id(user_id)
    
    async def find_users(self) -> List[UserResponse]:
        """Get all users"""
        return await self.user_repository.get_all_users()
    
    # Employability Operations
    async def update_employability_data(self, user_id: str, data: EmployabilityData) -> EmployabilityScore:
        """Update user's employability data and recalculate score"""
        # Ensure the data belongs to the correct user
        data.user_id = user_id
        
        # Save employability data
        await self.user_repository.save_employability_data(data)
        
        # Calculate new score
        score = self.employability_calculator.calculate_score(data)
        await self.user_repository.save_employability_score(score)
        
        # Generate new recommendations
        recommendations = self.recommendation_service.generate_recommendations(
            user_id, data, score
        )
        await self.user_repository.save_recommendations(recommendations)
        
        return score
    
    async def get_employability_score(self, user_id: str) -> Optional[EmployabilityScore]:
        """Get latest employability score for user"""
        return await self.user_repository.get_latest_employability_score(user_id)
    
    async def get_employability_data(self, user_id: str) -> Optional[EmployabilityData]:
        """Get employability data for user"""
        return await self.user_repository.get_employability_data(user_id)
    
    async def get_employability_history(self, user_id: str) -> List[EmployabilityScore]:
        """Get employability score history"""
        return await self.user_repository.get_employability_history(user_id)
    
    async def get_recommendations(self, user_id: str) -> List[Recommendation]:
        """Get recommendations for user"""
        return await self.user_repository.get_recommendations(user_id)
    
    # Reports and Analytics
    async def get_university_report(self, university: str) -> dict:
        """Get aggregated report for a university"""
        # This is a simplified implementation
        # In production, you'd want more sophisticated analytics
        all_users = await self.find_users()
        university_users = [u for u in all_users if u.university.lower() == university.lower()]
        
        if not university_users:
            return {"error": "No users found for this university"}
        
        # Calculate average scores for the university
        total_scores = []
        for user in university_users:
            score = await self.get_employability_score(str(user.id))
            if score:
                total_scores.append(score.overall_score)
        
        avg_score = sum(total_scores) / len(total_scores) if total_scores else 0
        
        return {
            "university": university,
            "total_students": len(university_users),
            "average_employability_score": round(avg_score, 2),
            "score_distribution": {
                "excellent": len([s for s in total_scores if s >= 80]),
                "good": len([s for s in total_scores if 60 <= s < 80]),
                "needs_improvement": len([s for s in total_scores if s < 60])
            }
        }

    def find_users(self) -> list[UserResponse]:
        return self.user_repo.find_users()
