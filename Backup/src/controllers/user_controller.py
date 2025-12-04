from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from ..models.user import UserResponse
from ..services.user_service import UserService
from ..repositories.user_repository import UserRepository
from ..config.db import get_database
from ..utils.auth import verify_token, get_credentials_exception

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
