import json
from google import genai
from google.genai import types
from sentence_transformers import SentenceTransformer
from app.core.config import settings

class AIService:
    def __init__(self):
        print("🤖 Inicializando Servicios de IA (Gemini 2.0 + Local)...")
        
        # 1. Cliente Gemini Moderno
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # 2. Modelo Local para Embeddings
        # Esto descarga el modelo "intfloat/multilingual-e5-base" la primera vez
        print(f"📥 Cargando modelo local: {settings.EMBEDDING_MODEL_NAME}...")
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        print("✅ IA lista.")

    def generate_embedding(self, text: str) -> list[float]:
        """Genera el vector matemático para una skill usando el modelo local."""
        try:
            clean_text = text.replace("\n", " ")
            # encode devuelve un numpy array, lo convertimos a lista
            embedding = self.embedding_model.encode(clean_text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            print(f"Error generando embedding local: {e}")
            # Fallback de seguridad (ceros) solo si falla el modelo
            return [0.0] * 768

    def extract_skills_from_text(self, cv_text: str) -> dict:
        """
        Usa Gemini para leer el CV y devolver JSON.
        """
        # PROMPT CORREGIDO:
        # Instrucción explícita para agrupar herramientas dentro de técnicas
        prompt = f"""
        Actúa como un experto reclutador IT. Analiza el siguiente texto de un CV.
        Extrae las habilidades y clasifícalas EXCLUSIVAMENTE en dos grupos:
        1. "habilidadesTecnicas": Incluye lenguajes, frameworks, software (Excel, Jira, SAP), herramientas y conocimientos técnicos.
        2. "habilidadesBlandas": Solo habilidades blandas,sociales, liderazgo e idiomas.

        NO uses la categoría "herramientas". Si es un software, va en técnicas.
        
        Responde estrictamente con este esquema JSON:
        {{
            "habilidadesTecnicas": ["Skill1", "Skill2"],
            "habilidadesBlandas": ["Skill1", "Skill2"]
        }}
        
        Texto del CV:
        ---
        {cv_text[:10000]}
        ---
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash", # O el modelo que tengas disponible
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            
            return json.loads(response.text)
            
        except Exception as e:
            print(f"❌ Error Gemini: {e}")
            return {"habilidadesTecnicas": [], "habilidadesBlandas": []}

ai_service = AIService()