from sqlmodel import SQLModel, create_engine, Session, text, select
from app.core.config import settings

# Importar modelos para que se registren en SQLModel
from app.models.user import User
from app.models.skill import Skill
from app.models.link import UserSkillLink
from app.models.job import JobPosting, JobSkillLink

# IMPORTAR MODELO PLAN
from app.models.plan import Plan

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

#  FUNCIÓN PARA AUTO-SEED de PLANES
def create_initial_plans():
    """Crea los planes por defecto si la tabla está vacía."""
    with Session(engine) as session:
        # Verificamos si ya existe al menos un plan
        if session.exec(select(Plan)).first():
            print("ℹ️ Los planes ya existen. Saltando seed.")
            return

        print("🌱 Base de datos de planes vacía. Creando planes por defecto...")
        
        plans_data = [
            Plan(
                code="TRIAL", 
                name="Plan Trial", 
                description="Prueba gratuita por 7 días", 
                price=0.0, 
                duration_days=7, 
                is_trial=True, 
                display_order=1, 
                features=["Acceso básico al dashboard", "Análisis de 5 habilidades", "1 reporte de empleabilidad"]
            ),
            Plan(
                code="MONTHLY", 
                name="Plan Mensual", 
                description="Plan de pago mensual", 
                price=29.90, 
                duration_days=30, 
                is_trial=False, 
                display_order=2, 
                features=["Acceso completo", "Análisis ilimitado", "Recomendaciones personalizadas", "Soporte prioritario"]
            ),
            Plan(
                code="ANNUAL", 
                name="Plan Anual", 
                description="Plan anual con descuento", 
                price=299.00, 
                duration_days=365, 
                is_trial=False, 
                display_order=3, 
                features=["Todo lo del Plan Mensual", "2 meses gratis", "Mentoría mensual", "Certificados"]
            )
        ]
        
        for plan in plans_data:
            session.add(plan)
        
        session.commit()
        print("✅ Planes creados exitosamente.")

def get_session():
    with Session(engine) as session:
        yield session