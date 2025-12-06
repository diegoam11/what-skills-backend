# Usamos una versión ligera de Python 3.11
FROM python:3.11-slim

# Evita que Python genere archivos .pyc y guarda logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /code

# Instalamos dependencias del sistema necesarias para compilar algunas librerías
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiamos primero los requerimientos (para aprovechar la caché de Docker)
COPY requirements.txt /code/

# Instalamos las librerías de Python
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# --- CORRECCIÓN IMPORTANTE ---
# Antes copiabas "src", ahora copiamos "app"
COPY ./app /code/app

# Usuario no-root por seguridad (opcional pero recomendado)
# RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /code
# USER appuser

# Comando para iniciar la app (apuntando a app.main)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]