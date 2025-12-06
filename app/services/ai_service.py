import json
import os
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
        # Usar ruta local si existe (Docker), sino descargar de HuggingFace (local dev)
        model_path = os.environ.get("MODEL_PATH", "/models/multilingual-e5-base")

        if os.path.exists(model_path):
            print(f"📥 Cargando modelo desde ruta local: {model_path}...")
            self.embedding_model = SentenceTransformer(model_path)
        else:
            print(f"📥 Descargando modelo: {settings.EMBEDDING_MODEL_NAME}...")
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        print("✅ IA lista.")

    def generate_embedding(self, text: str, is_document: bool = True) -> list[float]:
        """
        Genera el embedding usando los prefijos obligatorios de E5.
        - is_document=True -> 'passage: Texto...' (Para guardar ofertas en DB)
        - is_document=False -> 'query: Texto...' (Para buscar desde el perfil)
        """
        try:
            clean_text = text.replace("\n", " ")

            prefix = "passage: " if is_document else "query: "
            text_with_prefix = prefix + clean_text

            # encode devuelve un numpy array, lo convertimos a lista
            embedding = self.embedding_model.encode(clean_text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            print(f"Error generando embedding local: {e}")
            # Fallback de seguridad (ceros) solo si falla el modelo
            return [0.0] * 768

    def extract_skills_from_text(self, cv_text: str) -> dict:
        """
        Usa Gemini para leer el CV y devolver JSON con niveles estimados.
        """
        prompt = f"""
        Actúa como un experto reclutador IT. Analiza el siguiente CV.
        Extrae las habilidades y clasifícalas en técnicas y blandas.
        
        IMPORTANTE: Intenta deducir el nivel de experiencia en cada habilidad (Básico, Intermedio, Avanzado) basado en el contexto:
        - "Senior", "+5 años", "Experto", "Lideró" -> Avanzado
        - "Semi-Senior", "2-4 años", "Sólidos conocimientos" -> Intermedio
        - "Junior", "Becario", "Básico", "Aprendiendo" -> Básico
        - Si no hay contexto claro, asigna "Básico".

        Responde estrictamente con un JSON con  este formato:
        {{
            "habilidadesTecnicas": [
                {{"name": "Python", "proficiency": "Avanzado"}},
                {{"name": "SQL", "proficiency": "Intermedio"}}
            ],
            "habilidadesBlandas": [
                {{"name": "Liderazgo", "proficiency": "Avanzado"}}
            ]
        }}
        
        NO uses la categoría "herramientas".
        Texto del CV:
        ---
        {cv_text[:12000]} 
        ---
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash", 
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
        
        
    def extract_job_data_from_text(self, job_text: str) -> dict:
        """
        Analiza una oferta laboral y extrae título, skills requeridas y nivel.
        """
        prompt = f"""
        Actúa como un experto en RRHH. Analiza la siguiente oferta de trabajo.
        Extrae:
        1. Título del puesto (Si no es claro, deduce uno estandarizado).
        2. Habilidades Técnicas requeridas (y su nivel sugerido: Básico, Intermedio, Avanzado).
        3. Habilidades Blandas requeridas.
        
        Responde estrictamente en JSON:
        {{
            "title": "Nombre del Puesto",
            "company": "Nombre de la empresa (si aparece, sino 'Confidencial')",
            "technical_skills": [{{"name": "React", "proficiency": "Avanzado"}}],
            "soft_skills": [{{"name": "Comunicación", "proficiency": "Intermedio"}}]
        }}

        Oferta:
        ---
        {job_text[:10000]}
        ---
        """
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"❌ Error Gemini Job Extraction: {e}")
            # Retorno de emergencia
            return {"title": "Desconocido", "company": "Confidencial", "technical_skills": [], "soft_skills": []}

ai_service = AIService()