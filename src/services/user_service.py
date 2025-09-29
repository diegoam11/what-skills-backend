from models.user import UserResponse
from repositories.user_repository import UserRepository


class UserService:
    def __init__(self):
        self.user_repo = UserRepository()

    def find_users(self) -> list[UserResponse]:
        return self.user_repo.find_users()
