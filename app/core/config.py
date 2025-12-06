from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Configuración General
    PROJECT_NAME: str = "What Skills API"
    API_V1_STR: str = "/api/v1"
    
    # Seguridad (¡ESTO ES LO QUE FALTABA!)
    # Al definirlas aquí, Pydantic las buscará en tu archivo .env
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Base de Datos
    DATABASE_URL: str
    
    # IA - Gemini
    GEMINI_API_KEY: str
    
    # IA - Modelo Local
    EMBEDDING_MODEL_NAME: str = "intfloat/multilingual-e5-base"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()