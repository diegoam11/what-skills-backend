from sqlmodel import SQLModel, Field
from typing import Optional
import uuid

class UserSkillLink(SQLModel, table=True):
    # Claves foráneas que apuntan a las otras tablas
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id", primary_key=True)
    skill_id: Optional[int] = Field(default=None, foreign_key="skill.id", primary_key=True)
    
    # Datos propios de la relación
    level: str = "Básico" # 'Básico', 'Intermedio', 'Avanzado'
    verified: bool = False