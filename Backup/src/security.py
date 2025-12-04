import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

# --- Configuración de Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Configuración de JWT ---
# Las variables siguen siendo de tipo (str | None) aquí
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# El check en tiempo de ejecución. Si falta algo, la app no iniciará.
if not SECRET_KEY:
    raise EnvironmentError("SECRET_KEY no está configurado en el entorno.")
if not ALGORITHM:
    raise EnvironmentError("ALGORITHM no está configurado en el entorno.")


# Esto le dice a FastAPI cómo "pedir" un token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña plana contra su hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Genera un hash para una contraseña plana."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un nuevo token JWT."""
    
    # Añadimos este check para asegurarle al linter que las variables no son None.
    # Aunque el check de arriba ya lo hizo, esto satisface el análisis estático.
    if not SECRET_KEY or not ALGORITHM:
        raise ValueError("SECRET_KEY o ALGORITHM no están configurados")
    # --- FIN DE LA CORRECCIÓN ---

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Ahora el linter sabe que SECRET_KEY y ALGORITHM son strings
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- Dependencia de FastAPI ---

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """
    Dependencia de FastAPI para proteger rutas.
    Valida el token y extrae el ID del usuario (el 'sub').
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # --- INICIO DE LA CORRECCIÓN ---
        # También añadimos el check aquí
        if not SECRET_KEY or not ALGORITHM:
            raise ValueError("SECRET_KEY o ALGORITHM no están configurados")
        # --- FIN DE LA CORRECCIÓN ---

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        user_id: str = payload.get("sub") # type: ignore
        if user_id is None:
            raise credentials_exception
            
    except (JWTError, ValidationError, ValueError): # Añadimos ValueError
        raise credentials_exception
        
    return user_id