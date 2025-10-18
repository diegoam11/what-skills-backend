from fastapi import APIRouter

from src.models.user import UserCreate, UserResponse
from src.services.user_service import UserService

router = APIRouter()

user_service = UserService()


@router.get("/users")
async def find_user() -> list[UserResponse]:
    return user_service.find_users()


@router.post("/users")
async def create_user(user: UserCreate) -> UserResponse:
    return user_service.create_user(user)
