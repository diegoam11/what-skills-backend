from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
import uuid
from sqlmodel import SQLModel, Field, Relationship

# Importamos el Link Model directamente (este no causa ciclos)
from app.models.link import UserSkillLink

if TYPE_CHECKING:
    from app.models.skill import Skill

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str
    
    full_name: Optional[str] = None
    role: str = Field(default="user")
    
    career_target: Optional[str] = None
    job_target: Optional[str] = None
    academic_level: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relación: Un usuario tiene muchas skills
    # Usamos "Skill" (string)
    skills: List["Skill"] = Relationship(back_populates="users", link_model=UserSkillLink)