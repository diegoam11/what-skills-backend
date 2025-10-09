from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..models.user import UserLogin, UserCreate, UserResponse, Token
from ..services.user_service import UserService
from ..repositories.user_repository import UserRepository
from ..config.db import get_database
from ..utils.auth import verify_token, get_credentials_exception

router = APIRouter(prefix="/auth", tags=["Authentication"])
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


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """Register a new user"""
    try:
        user = await user_service.register_user(user_data)
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    user_service: UserService = Depends(get_user_service)
):
    """Login user and return access token"""
    try:
        token = await user_service.login_user(login_data)
        return token
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user_email: str = Depends(get_current_user_email),
    user_service: UserService = Depends(get_user_service)
):
    """Get current user information"""
    user = await user_service.get_user_by_email(current_user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user