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

    # 1. Vectorizar objetivo (SIMPLE)
    try:
        # Usamos el input del usuario tal cual.
        # Mantenemos is_document=False solo porque E5 lo requiere técnicamente ("query: "), 
        # pero no agregamos palabras extra.
        query_vector = ai_service.generate_embedding(target, is_document=False)
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
    
    # --- FILTRO POR DISTANCIA (ÚNICO FILTRO) ---
    # Ajustamos a 0.28 como acordamos.
    # Si ves que sigue entrando "basura", bájalos a 0.26 o 0.25 poco a poco.
    MAX_DISTANCE_THRESHOLD = 0.28
    
    valid_jobs = []
    print(f"\n🔍 Analizando objetivo: '{target}'")
    print("-" * 50)
    
    for row in raw_results:
        # Solo miramos la distancia matemática
        if row.distance <= MAX_DISTANCE_THRESHOLD:
            valid_jobs.append(row)
            print(f"   ✅ Aceptada: {row.title} ({row.distance:.4f})")
        else:
            print(f"   ❌ Descartada por distancia: {row.title} ({row.distance:.4f})")

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
        if skill.name not in skill_market_stats:
            skill_market_stats[skill.name] = {"count": 0, "levels": []}
        
        skill_market_stats[skill.name]["count"] += 1
        skill_market_stats[skill.name]["levels"].append(link.level)

    # 4. Obtener Skills del Usuario
    user_links = session.exec(select(UserSkillLink, Skill).where(
        UserSkillLink.user_id == current_user.id,
        UserSkillLink.skill_id == Skill.id
    )).all()
    
    user_skills_map = {skill.name: link.level for link, skill in user_links}
    
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
        
        if skill_name in user_skills_map:
            present_skills.append({
                "name": skill_name,
                "level": user_skills_map[skill_name]
            })
            user_matched_weight += weight 
        else:
            missing_skills.append({
                "name": skill_name,
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