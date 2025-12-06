from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, ValidationInfo, AnyUrl

class Settings(BaseSettings):
    # Configuración General
    PROJECT_NAME: str = "What Skills API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "local" # Útil para saber dónde estamos

    # Seguridad
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # --- VARIABLES PARA CLOUD SQL (Opcionales) ---
    # Estas se llenarán automáticamente desde Cloud Run
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_NAME: Optional[str] = None
    INSTANCE_CONNECTION_NAME: Optional[str] = None

    # --- BASE DE DATOS ---
    # La hacemos opcional para poder construirla si falta
    DATABASE_URL: Optional[str] = None
    
    # IA
    GEMINI_API_KEY: str
    EMBEDDING_MODEL_NAME: str = "intfloat/multilingual-e5-base"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    # VALIDADOR: Construye la URL si no existe, basándose en el entorno
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> AnyUrl:
        # 1. Si ya viene una URL (caso Local/.env), la usamos tal cual
        if isinstance(v, str) and v:
            return v
        
        # 2. Si no hay URL, intentamos armarla con las variables de Cloud SQL
        # Recuperamos los valores ya validados del modelo
        values = info.data
        
        # Nota: En Pydantic v2, info.data contiene los valores previos.
        # Si esto falla, accedemos a os.environ como fallback, 
        # pero normalmente info.data debería tenerlo si el orden es correcto o usamos model_validator.
        
        # Para mayor seguridad usamos un fallback directo a las variables si info.data no las tiene aún
        import os
        db_user = values.get("DB_USER") or os.getenv("DB_USER")
        db_pass = values.get("DB_PASSWORD") or os.getenv("DB_PASSWORD")
        db_name = values.get("DB_NAME") or os.getenv("DB_NAME")
        instance = values.get("INSTANCE_CONNECTION_NAME") or os.getenv("INSTANCE_CONNECTION_NAME")

        if db_user and db_pass and db_name and instance:
            # Construcción para Cloud SQL (Unix Socket) con driver psycopg2 (default de SQLModel)
            return f"postgresql://{db_user}:{db_pass}@/{db_name}?host=/cloudsql/{instance}"
        
        raise ValueError("Falta la configuración de Base de Datos (DATABASE_URL o variables Cloud SQL)")

settings = Settings()