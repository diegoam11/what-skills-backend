from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from models.user import EmployabilityData, EmployabilityScore, Recommendation
from services.user_service import UserService
from repositories.user_repository import UserRepository
from config.db import get_database
from utils.auth import verify_token, get_credentials_exception

router = APIRouter(prefix="/employability", tags=["Employability"])
security = HTTPBearer()


async def get_user_service():
    """Dependency to get user service with database connection"""
    database = await get_database()
    user_repository = UserRepository(database)
    return UserService(user_repository)


async def get_current_user_email(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Dependency to get current user email from token"""
    return verify_token(credentials.credentials, get_credentials_exception())


@router.get("/score", response_model=EmployabilityScore)
async def get_employability_score(
    current_user_email: str = Depends(get_current_user_email),
    user_service: UserService = Depends(get_user_service)
):
    """Get current user's employability score"""
    user = await user_service.get_user_by_email(current_user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    score = await user_service.get_employability_score(str(user.id))
    if not score:
        raise HTTPException(status_code=404, detail="Employability score not found")
    
    return score


@router.get("/data", response_model=EmployabilityData)
async def get_employability_data(
    current_user_email: str = Depends(get_current_user_email),
    user_service: UserService = Depends(get_user_service)
):
    """Get current user's employability data"""
    user = await user_service.get_user_by_email(current_user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    data = await user_service.get_employability_data(str(user.id))
    if not data:
        raise HTTPException(status_code=404, detail="Employability data not found")
    
    return data


@router.post("/data", response_model=EmployabilityScore)
async def update_employability_data(
    data: EmployabilityData,
    current_user_email: str = Depends(get_current_user_email),
    user_service: UserService = Depends(get_user_service)
):
    """Update user's employability data and recalculate score"""
    user = await user_service.get_user_by_email(current_user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        score = await user_service.update_employability_data(str(user.id), data)
        return score
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update employability data: {str(e)}"
        )


@router.get("/history", response_model=List[EmployabilityScore])
async def get_employability_history(
    current_user_email: str = Depends(get_current_user_email),
    user_service: UserService = Depends(get_user_service)
):
    """Get user's employability score history"""
    user = await user_service.get_user_by_email(current_user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    history = await user_service.get_employability_history(str(user.id))
    return history


@router.get("/recommendations", response_model=List[Recommendation])
async def get_recommendations(
    current_user_email: str = Depends(get_current_user_email),
    user_service: UserService = Depends(get_user_service)
):
    """Get personalized recommendations for the user"""
    user = await user_service.get_user_by_email(current_user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    recommendations = await user_service.get_recommendations(str(user.id))
    return recommendations