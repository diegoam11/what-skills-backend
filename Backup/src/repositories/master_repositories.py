from bson import ObjectId
from typing import Optional, List
from src.config.db import get_mongo_connection

# --- Modelo Base (Opcional pero recomendado) ---
# Necesitarás crear modelos Pydantic simples para esto en, 
# por ejemplo, src/models/master_data.py
# class Career(BaseModel):
#     id: str = Field(alias="_id")
#     code: str
#     name: str
#     ...

class BaseMasterRepository:
    """Clase base genérica para todos los repositorios maestros."""
    def __init__(self, collection_name: str):
        mongo_conn = get_mongo_connection()
        self.collection = mongo_conn.get_collection("what-skills-db", collection_name)

    def find_by_id(self, id_str: str) -> Optional[dict]:
        """Busca un documento por su ID (string)."""
        try:
            object_id = ObjectId(id_str)
            return self.collection.find_one({"_id": object_id})
        except Exception:
            return None

    def find_by_code(self, code: str) -> Optional[dict]:
        """Busca un documento por su 'code'."""
        return self.collection.find_one({"code": code})

    def find_all_active(self) -> List[dict]:
        """Devuelve todos los documentos activos."""
        documents = list(self.collection.find({"isActive": True}))
        for doc in documents:
            if "_id" in doc and isinstance(doc["_id"], ObjectId):
                doc["_id"] = str(doc["_id"])
        return documents

# --- Implementaciones Específicas ---

class CareerRepository(BaseMasterRepository):
    def __init__(self):
        super().__init__("masterCareers")

class PositionRepository(BaseMasterRepository):
    def __init__(self):
        super().__init__("masterPositions")

class UniversityRepository(BaseMasterRepository):
    def __init__(self):
        super().__init__("masterUniversities")

class IndustryRepository(BaseMasterRepository):
    def __init__(self):
        super().__init__("masterIndustries")

class SkillRepository(BaseMasterRepository):
    def __init__(self):
        super().__init__("masterSkills")