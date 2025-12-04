from src.models.user import UserCreate, UserResponse
from src.repositories.user_repository import UserRepository


class UserService:
    def __init__(self):
        self.user_repo = UserRepository()

    def find_users(self) -> list[UserResponse]:
        return self.user_repo.find_users()

    def create_user(self, user: UserCreate) -> UserResponse:
        return self.user_repo.create_user(user)
