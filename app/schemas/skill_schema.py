from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class SkillsExtractionResponse(BaseModel):
    habilidadesTecnicas: List[str]
    habilidadesBlandas: List[str]


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