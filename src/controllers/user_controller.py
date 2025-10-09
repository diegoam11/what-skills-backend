from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from ..models.user import UserResponse
from ..services.user_service import UserService
from ..repositories.user_repository import UserRepository
from ..config.db import get_database
from ..utils.auth import verify_token, get_credentials_exception

router = APIRouter(prefix="/users", tags=["Users"])
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


@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    current_user_email: str = Depends(get_current_user_email),
    user_service: UserService = Depends(get_user_service)
):
    """Get all users (authenticated endpoint)"""
    try:
        users = await user_service.find_users()
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user_email: str = Depends(get_current_user_email),
    user_service: UserService = Depends(get_user_service)
):
    """Get user by ID"""
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
