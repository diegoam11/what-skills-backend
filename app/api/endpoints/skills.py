from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from app.services.pdf_service import pdf_service
from app.services.ai_service import ai_service
# Importamos el Schema actualizado
from app.schemas.skill_schema import SkillsExtractionResponse, SkillAddRequest
from typing import List
from sqlmodel import Session, select
from app.core.database import get_session
from app.api.endpoints.auth import get_current_user
from app.models.user import User
from app.models.skill import Skill
from app.models.link import UserSkillLink

router = APIRouter()

@router.post("/extract-from-cv", response_model=SkillsExtractionResponse)
async def extract_skills_from_cv(
    file: UploadFile = File(...)
):
    """
    Recibe un PDF, extrae el texto y utiliza IA para identificar habilidades.
    """
    # 1. Extraer texto
    cv_text = await pdf_service.extract_text_from_upload(file)
    
    # 2. Procesar con IA
    try:
        skills_data = ai_service.extract_skills_from_text(cv_text)
        return skills_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me", response_model=List[SkillAddRequest])
def get_my_skills(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Obtiene las habilidades del usuario logueado"""
    statement = select(Skill, UserSkillLink).where(
        UserSkillLink.user_id == current_user.id,
        UserSkillLink.skill_id == Skill.id
    )
    results = session.exec(statement).all()
    
    my_skills = []
    for skill, link in results:
        my_skills.append({
            "name": skill.name,
            # Asegúrate de limpiar tu DB de categorías antiguas o esto dará error
            "category": skill.category, 
            "proficiency": link.level
        })
    return my_skills


@router.post("/me", response_model=SkillAddRequest)
def add_skill_to_me(
    skill_in: SkillAddRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Agrega una habilidad al usuario y genera su vector si es nueva."""
    
    # 1. Buscar si la habilidad ya existe en el maestro global
    existing_skill = session.exec(select(Skill).where(Skill.name == skill_in.name)).first()
    
    if not existing_skill:
        # --- CORRECCIÓN: GENERACIÓN DE EMBEDDINGS ---
        # Llamamos al servicio para obtener el vector real
        vector = ai_service.generate_embedding(skill_in.name)
        
        new_skill = Skill(
            name=skill_in.name, 
            category=skill_in.category, 
            embedding=vector # Guardamos el vector real (no ceros)
        ) 
        session.add(new_skill)
        session.commit()
        session.refresh(new_skill)
        existing_skill = new_skill
    
    # 2. Verificar enlace con usuario
    link = session.exec(select(UserSkillLink).where(
        UserSkillLink.user_id == current_user.id,
        UserSkillLink.skill_id == existing_skill.id
    )).first()
    
    if link:
        link.level = skill_in.proficiency
        session.add(link)
    else:
        new_link = UserSkillLink(
            user_id=current_user.id,
            skill_id=existing_skill.id,
            level=skill_in.proficiency
        )
        session.add(new_link)
    
    session.commit()
    return skill_in


@router.delete("/me/{skill_name:path}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill_from_me(
    skill_name: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Elimina la habilidad del perfil del usuario (NO de la base de datos global)"""
    
    # 1. Buscamos la skill por nombre
    skill = session.exec(select(Skill).where(Skill.name == skill_name)).first()
    
    if not skill:
        raise HTTPException(status_code=404, detail="Habilidad no encontrada")

    # 2. Buscamos el enlace específico de este usuario
    link = session.exec(select(UserSkillLink).where(
        UserSkillLink.user_id == current_user.id,
        UserSkillLink.skill_id == skill.id
    )).first()

    if not link:
        raise HTTPException(status_code=404, detail="No tienes esta habilidad en tu perfil")

    # 3. Borramos el enlace
    session.delete(link)
    session.commit()
    return None