# Usamos una imagen base ligera de Python (ajusta la versión si es necesario)
FROM python:3.11-slim

# Evita que Python genere archivos .pyc y asegura que los logs lleguen a Cloud Logging inmediatamente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio donde se cachearán los modelos de HuggingFace (fuera de /app para no ser sobrescrito)
ENV HF_HOME=/models
ENV SENTENCE_TRANSFORMERS_HOME=/models

WORKDIR /app

# Copiamos primero los requirements para aprovechar la caché de Docker
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# PRE-DESCARGA del modelo de embeddings durante el build (evita rate limiting en runtime)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-base')"

# Copiamos el resto del código
COPY . .

# Exponemos el puerto (Cloud Run inyecta la variable PORT, por defecto 8080)
ENV PORT=8080

# Comando de ejecución con Uvicorn
# 'main:app' asume que tu archivo es main.py y la instancia de FastAPI es app
CMD exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1