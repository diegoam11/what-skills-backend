from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from app.models.link import UserSkillLink


if TYPE_CHECKING:
    from app.models.user import User

class Skill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    category: str 
    
    # 768 es la dimensión del modelo E5-Base
    embedding: List[float] = Field(sa_column=Column(Vector(768))) 

    # CORRECCIÓN AQUÍ:
    # 1. Usamos "User" como string (para evitar el error 'User not defined')
    # 2. Usamos UserSkillLink como CLASE (sin comillas) para arreglar el error de inspección
    users: List["User"] = Relationship(back_populates="skills", link_model=UserSkillLink)
