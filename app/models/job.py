from typing import Optional, List
from datetime import datetime
import uuid
from sqlmodel import SQLModel, Field, Relationship
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column

# Tabla intermedia: Muchos Trabajos tienen Muchas Skills
class JobSkillLink(SQLModel, table=True):
    job_id: Optional[uuid.UUID] = Field(default=None, foreign_key="jobposting.id", primary_key=True)
    skill_id: Optional[int] = Field(default=None, foreign_key="skill.id", primary_key=True)
    level: str = "Intermedio" # Nivel requerido para esta skill en este trabajo

class JobPosting(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    title: str
    company: str
    description: str # Texto completo sucio
    url: Optional[str] = None
    source: str # 'LinkedIn', 'Bumeran'
    location: str = "Remoto"
    
    posted_date: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    # Vector para búsqueda semántica (mismo tamaño que Skill: 768 para E5-Base)
    embedding: List[float] = Field(sa_column=Column(Vector(768)))