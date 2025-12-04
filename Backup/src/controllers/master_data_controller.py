from fastapi import APIRouter
from typing import List, Dict, Any
from src.repositories.master_repositories import (
    CareerRepository,
    PositionRepository,
    UniversityRepository,
    IndustryRepository,
    SkillRepository,
)

router = APIRouter(prefix="/master-data", tags=["Master Data"])

# Instanciamos los repositorios
career_repo = CareerRepository()
position_repo = PositionRepository()
university_repo = UniversityRepository()
industry_repo = IndustryRepository()
skill_repo = SkillRepository()

# NOTA: Deberías crear modelos Pydantic (ej. CareerResponse)
# para la respuesta, pero por ahora devolveremos un diccionario.

@router.get("/careers", response_model=List[Dict[str, Any]])
async def get_all_careers():
    """Devuelve todas las carreras activas."""
    return career_repo.find_all_active()

@router.get("/positions", response_model=List[Dict[str, Any]])
async def get_all_positions():
    """Devuelve todas las posiciones activas."""
    return position_repo.find_all_active()

@router.get("/universities", response_model=List[Dict[str, Any]])
async def get_all_universities():
    """Devuelve todas las universidades activas."""
    return university_repo.find_all_active()

@router.get("/industries", response_model=List[Dict[str, Any]])
async def get_all_industries():
    """Devuelve todas las industrias activas."""
    return industry_repo.find_all_active()

@router.get("/skills", response_model=List[Dict[str, Any]])
async def get_all_skills():
    """Devuelve todas las habilidades activas."""
    return skill_repo.find_all_active()