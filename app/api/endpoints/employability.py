from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, text
from app.core.database import get_session
from app.api.endpoints.auth import get_current_user
from app.models.user import User
from app.models.job import JobPosting, JobSkillLink
from app.models.skill import Skill
from app.models.link import UserSkillLink
from app.services.ai_service import ai_service
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlmodel import col

router = APIRouter()

# --- Modelos de Respuesta ---
class GapItem(BaseModel):
    name: str
    level_required: str
    frequency: int
    reason: str 

class SkillMatch(BaseModel):
    name: str
    level: str

class EmployabilityReport(BaseModel):
    score: int 
    market_fit: str 
    analyzed_jobs: int
    top_missing_skills: List[GapItem]
    top_present_skills: List[SkillMatch]
    analyzed_job_titles: List[str] 

@router.get("/analyze", response_model=EmployabilityReport)
async def analyze_profile(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    target = current_user.job_target or current_user.career_target
    if not target:
        raise HTTPException(status_code=400, detail="Debes definir un Objetivo Profesional.")

    # 1. Vectorizar objetivo
    enhanced_target = f"Ingeniería de software programación desarrollo técnico sistemas {target}"
    
    try:
        query_vector = ai_service.generate_embedding(enhanced_target, is_document=False)
    except Exception as e:
        print(f"Error embedding: {e}")
        query_vector = [0.0] * 768 

    # 2. Búsqueda Semántica
    query = text("""
        SELECT id, title, embedding <=> :vector AS distance
        FROM jobposting
        ORDER BY distance ASC
        LIMIT 20
    """)
    
    result_proxy = session.execute(query, params={"vector": str(query_vector)})
    raw_results = result_proxy.fetchall()
    
    # --- FILTRO ---
    MAX_DISTANCE_THRESHOLD = 0.28
    
    valid_jobs = []
    
    for row in raw_results:
        if row.distance <= MAX_DISTANCE_THRESHOLD:
            valid_jobs.append(row)

    if not valid_jobs:
        return {
            "score": 0,
            "market_fit": "Sin datos relevantes",
            "analyzed_jobs": 0,
            "top_missing_skills": [],
            "top_present_skills": [],
            "analyzed_job_titles": []
        }

    job_ids = [row.id for row in valid_jobs]
    job_titles = [row.title for row in valid_jobs]
    
    # 3. Obtener Skills del Mercado
    statement = select(JobSkillLink, Skill).join(Skill).where(
        JobSkillLink.job_id.in_(job_ids) # type: ignore
    )
    market_skills_rows = session.exec(statement).all()
    
    skill_market_stats: Dict[str, Dict[str, Any]] = {}
    
    for link, skill in market_skills_rows:
        # Usamos el nombre original para mostrar, pero la clave será LOWER para agrupar mejor
        # (Aunque aquí confiamos en que la IA normalizó, pero por si acaso)
        skill_name = skill.name
        
        if skill_name not in skill_market_stats:
            skill_market_stats[skill_name] = {"count": 0, "levels": []}
        
        skill_market_stats[skill_name]["count"] += 1
        skill_market_stats[skill_name]["levels"].append(link.level)

    # 4. Obtener Skills del Usuario (MAPEO INSENSIBLE A MAYÚSCULAS)
    user_links = session.exec(select(UserSkillLink, Skill).where(
        UserSkillLink.user_id == current_user.id,
        UserSkillLink.skill_id == Skill.id
    )).all()
    
    # --- CORRECCIÓN CLAVE AQUÍ ---
    # Guardamos las keys en minúsculas para facilitar la búsqueda
    # Guardamos también el nombre "bonito" original para mostrarlo luego
    user_skills_map = {
        skill.name.lower(): {"level": link.level, "original_name": skill.name} 
        for link, skill in user_links
    }
    
    # 5. CALCULAR GAPS
    missing_skills = []
    present_skills = []
    total_market_weight = 0
    user_matched_weight = 0
    
    min_freq_threshold = max(1, len(valid_jobs) * 0.2)
    
    sorted_market_skills = sorted(
        skill_market_stats.items(), 
        key=lambda x: x[1]['count'], 
        reverse=True
    )

    for skill_name, stats in sorted_market_skills:
        if stats['count'] < min_freq_threshold:
            continue
            
        weight = stats['count']
        total_market_weight += weight
        
        levels = stats['levels']
        required_level = max(set(levels), key=levels.count)
        
        # --- COMPARACIÓN INSENSIBLE A MAYÚSCULAS ---
        name_lower = skill_name.lower()
        
        if name_lower in user_skills_map:
            # ¡MATCH ENCONTRADO!
            user_skill_data = user_skills_map[name_lower]
            
            present_skills.append({
                "name": user_skill_data["original_name"], # Mostramos el nombre que tiene el usuario
                "level": user_skill_data["level"]
            })
            user_matched_weight += weight 
        else:
            # GAP REAL
            missing_skills.append({
                "name": skill_name, # Mostramos el nombre como lo pide el mercado
                "level_required": required_level,
                "frequency": stats['count'],
                "reason": f"Aparece en {stats['count']} de {len(valid_jobs)} ofertas"
            })

    # 6. Score
    score = 0
    if total_market_weight > 0:
        score = int((user_matched_weight / total_market_weight) * 100)
    
    if score >= 80: fit = "Alto"
    elif score >= 50: fit = "Medio"
    else: fit = "Bajo"

    return {
        "score": score,
        "market_fit": fit,
        "analyzed_jobs": len(valid_jobs),
        "top_missing_skills": missing_skills[:6],
        "top_present_skills": present_skills,
        "analyzed_job_titles": job_titles
    }