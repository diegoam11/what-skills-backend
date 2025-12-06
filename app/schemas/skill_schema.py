from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class ExtractedSkill(BaseModel):
    name: str
    # La IA intentará adivinar, si no sabe, por defecto Básico
    proficiency: Literal["Básico", "Intermedio", "Avanzado"] = "Básico"

class SkillsExtractionResponse(BaseModel):
    habilidadesTecnicas: List[ExtractedSkill]
    habilidadesBlandas: List[ExtractedSkill]


class SkillAddRequest(BaseModel):
    name: str
    proficiency: str # "Básico", "Intermedio", "Avanzado"
    
    # ESTO ES LO NUEVO:
    # Restricción estricta: Solo acepta "técnica" o "blanda".
    # Si intentan mandar "herramienta", la API dará error automáticamente.
    category: Literal["técnica", "blanda"] = Field(
        ..., 
        description="Usa 'técnica' para hard skills y software. Usa 'blanda' solo para soft skills."
    )