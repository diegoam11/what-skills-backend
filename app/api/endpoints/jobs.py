from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.services.ai_service import ai_service
from app.models.job import JobPosting, JobSkillLink
from app.models.skill import Skill
from app.models.user import User
from app.api.endpoints.auth import get_current_user
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# Schema para recibir el texto (Input)
class JobIngestRequest(BaseModel):
    raw_text: str
    url: Optional[str] = None
    source: str = "Manual"

# Schema para responder (Output)
class JobIngestResponse(BaseModel):
    id: str
    title: str
    skills_found: int
    message: str

@router.post("/ingest", response_model=JobIngestResponse)
async def ingest_job_offer(
    data: JobIngestRequest,
    session: Session = Depends(get_session),
    # Opcional: Solo admins pueden hacer esto
    # current_user: User = Depends(get_current_active_superuser) 
):
    """
    Recibe el texto de una oferta, la analiza con IA, vectoriza y guarda.
    """
    if not data.raw_text.strip():
        raise HTTPException(status_code=400, detail="El texto de la oferta no puede estar vacío")

    print(f"🧠 Analizando oferta de origen: {data.source}...")
    
    # 1. Extracción de datos con Gemini
    extracted_data = ai_service.extract_job_data_from_text(data.raw_text)

    # Si Gemini devolvió una lista por error (ej: [{...}]), tomamos el primer elemento.
    if isinstance(extracted_data, list):
        if len(extracted_data) > 0:
            extracted_data = extracted_data[0]
        else:
            extracted_data = {} # Lista vacía -> Diccionario vacío

    # Si por alguna razón sigue sin ser dict (ej: string), forzamos vacío
    if not isinstance(extracted_data, dict):
        print(f"⚠️ Formato inesperado de Gemini: {type(extracted_data)}")
        extracted_data = {} 
    # --------------------------------

    
    # 2. Vectorización (Embedding) con E5 (Local)
    # Usamos try-except para que no falle si el modelo tiene problemas
    try:
        # IMPORTANTE: is_document=True agrega "passage: " al inicio para E5
        vector = ai_service.generate_embedding(data.raw_text, is_document=True)
    except Exception as e:
        print(f"⚠️ Error vectorizando oferta: {e}")
        vector = [0.0] * 768 # Fallback: Vector vacío para no romper la base de datos
    
    # 3. Guardar el JobPosting
    new_job = JobPosting(
        title=extracted_data.get("title", "Sin título"),
        company=extracted_data.get("company", "Confidencial"),
        description=data.raw_text,
        url=data.url,
        source=data.source,
        embedding=vector # <--- Aquí guardamos el vector para el matching
    )
    session.add(new_job)
    session.commit()
    session.refresh(new_job)
    
    # 4. Procesar y Enlazar Skills (JobSkillLink)
    all_extracted_skills = extracted_data.get("technical_skills", []) + extracted_data.get("soft_skills", [])
    
    skills_linked_count = 0
    
    for skill_item in all_extracted_skills:
        s_name = skill_item["name"]
        s_level = skill_item.get("proficiency", "Intermedio")
        
        # A. Buscar si la skill existe en la DB global, si no, crearla
        skill_db = session.exec(select(Skill).where(Skill.name == s_name)).first()
        
        if not skill_db:
            # Si es nueva, generamos su vector individual también
            try:
                # Para skills cortas, podemos usar is_document=False (query) o True, 
                # pero el manejo de error es lo vital aquí.
                skill_vector = ai_service.generate_embedding(s_name, is_document=False)
            except Exception:
                skill_vector = [0.0] * 768

            skill_db = Skill(
                name=s_name, 
                category="técnica", # Simplificación
                embedding=skill_vector
            )
            session.add(skill_db)
            session.commit()
            session.refresh(skill_db)
            
        # B. Crear el enlace Job <-> Skill (Evitando duplicados)
        # Verificamos si ya existe el link para este job y skill
        link_exists = session.exec(select(JobSkillLink).where(
            JobSkillLink.job_id == new_job.id,
            JobSkillLink.skill_id == skill_db.id
        )).first()

        if not link_exists:
            link = JobSkillLink(
                job_id=new_job.id,
                skill_id=skill_db.id,
                level=s_level
            )
            session.add(link)
            skills_linked_count += 1
        
    session.commit()
    
    return {
        "id": str(new_job.id),
        "title": new_job.title,
        "skills_found": skills_linked_count,
        "message": "Oferta procesada y vectorizada con éxito"
    }