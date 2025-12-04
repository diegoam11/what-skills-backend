from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    career: str
    position: str


class UserResponse(BaseModel):
    id: str = Field(..., alias="_id")
    email: EmailStr

    class Config:
        populate_by_name = True
