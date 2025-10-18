from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, _source_type: Any, _handler) -> dict:
        return {"type": "string"}

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)


# Authentication Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    career: str
    position: str


class UserResponse(BaseModel):
    id: str = Field(..., alias="_id")
    email: EmailStr

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class EmployabilityScore(BaseModel):
    user_id: PyObjectId
    overall_score: float = Field(..., ge=0.0, le=100.0)
    technical_score: float = Field(..., ge=0.0, le=100.0)
    experience_score: float = Field(..., ge=0.0, le=100.0)
    education_score: float = Field(..., ge=0.0, le=100.0)
    soft_skills_score: float = Field(..., ge=0.0, le=100.0)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# Recommendation Models
class Recommendation(BaseModel):
    user_id: PyObjectId
    type: str  # skill, course, networking, job
    title: str
    description: str
    priority: int = Field(..., ge=1, le=5)  # 1=highest, 5=lowest
    category: str
    url: Optional[str] = None
    estimated_impact: float = Field(..., ge=0.0, le=10.0)  # Expected score improvement
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# Token Models
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
