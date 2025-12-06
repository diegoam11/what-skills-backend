from sqlmodel import SQLModel, create_engine, Session, text
from app.core.config import settings

# Importar modelos para que se registren en SQLModel
from app.models.user import User
from app.models.skill import Skill
from app.models.link import UserSkillLink
from app.models.job import JobPosting, JobSkillLink

engine = create_engine(
    settings.DATABASE_URL,
    echo=True, # Logs SQL en consola (útil en dev)
    pool_pre_ping=True
)

def init_db():
    # 1. ACTIVAR LA EXTENSIÓN VECTOR
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    
    # 2. Crear las tablas
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session