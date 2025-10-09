from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# Authentication Models
class UserCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    career: str = Field(..., min_length=1, max_length=100)
    university: str = Field(..., min_length=1, max_length=100)
    semester: int = Field(..., ge=1, le=12)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    first_name: str
    last_name: str
    email: EmailStr
    career: str
    university: str
    semester: int
    created_at: datetime
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# Employability Models
class Skill(BaseModel):
    name: str
    category: str  # technical, soft, language
    proficiency: int = Field(..., ge=1, le=5)  # 1-5 scale


class Experience(BaseModel):
    title: str
    company: str
    duration_months: int
    description: str
    skills_used: List[str] = []


class Education(BaseModel):
    degree: str
    institution: str
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    graduation_year: Optional[int] = None


class EmployabilityData(BaseModel):
    user_id: PyObjectId = Field(alias="_id")
    skills: List[Skill] = []
    experiences: List[Experience] = []
    education: List[Education] = []
    projects: List[str] = []  # Project descriptions
    certifications: List[str] = []
    languages: List[str] = []
    updated_at: datetime = Field(default_factory=datetime.utcnow)

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
