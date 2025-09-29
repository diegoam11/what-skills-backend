from fastapi import APIRouter

from models.user import UserResponse
from services.user_service import UserService

router = APIRouter()

user_service = UserService()


@router.get("/user")
async def find_user() -> list[UserResponse]:
    return user_service.find_users()
