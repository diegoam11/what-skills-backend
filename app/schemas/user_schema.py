from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None
    career_target: str | None = None
    job_target: str | None = None

class UserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str | None
    role: str
    job_target: str | None = None
    career_target: str | None = None
    academic_level: str | None = None
    plan_code: str = "TRIAL" 
    subscription_status: str = "active"
    subscription_end: Optional[datetime] = None

class UserUpdate(BaseModel):
    full_name: str | None = None
    job_target: str | None = None
    career_target: str | None = None
    academic_level: str | None = None
    # Opcional: password para permitir cambiarlas