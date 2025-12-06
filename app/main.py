from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import init_db
from app.core.config import settings
# Importamos el servicio de IA para que se cargue el modelo al inicio
from app.services.ai_service import ai_service 
from app.api.api_v1 import api_router

from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando...")
    init_db()
    # Aquí podríamos hacer un "warm-up" de la IA si quisiéramos
    yield
    print("🛑 Apagando...")

app = FastAPI(title="What Skills API", lifespan=lifespan)


# --- CONFIGURAR CORS ---
# Permitimos que el Frontend (Vite) hable con el Backend
origins = [
    "http://localhost:5173",
    "http://localhost:3000", # Por si acaso
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permitir todos los métodos (POST, GET, etc)
    allow_headers=["*"], # Permitir todos los headers
)


app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"status": "online", "ai_model": "loaded"}