from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserRead, UserUpdate
from pydantic import BaseModel
from jose import jwt
from app.core.config import settings

router = APIRouter()

# Schema para el Token
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema para Login (Email/Pass)
class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register", response_model=UserRead)
def register(user_in: UserCreate, session: Session = Depends(get_session)):
    # (Este ya lo tenías, déjalo igual pero asegúrate de usar get_password_hash)
    existing_user = session.exec(select(User).where(User.email == user_in.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password), # Usamos la func de security.py
        full_name=user_in.full_name,
        career_target=user_in.career_target,
        job_target=user_in.job_target
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, session: Session = Depends(get_session)):
    """
    Inicia sesión con Email y Contraseña. Devuelve un JWT.
    """
    # 1. Buscar usuario
    user = session.exec(select(User).where(User.email == login_data.email)).first()
    
    # 2. Verificar password
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )
    
    # 3. Generar Token
    access_token = create_access_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


from fastapi.security import OAuth2PasswordBearer
# Esto le dice a FastAPI dónde buscar el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")
        
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.get("/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Obtiene los datos del usuario logueado usando el Token.
    """
    return current_user

@router.put("/me", response_model=UserRead)
def update_user_me(
    user_update: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza el perfil del usuario logueado.
    """
    # Actualizamos solo los campos que vengan con datos
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.job_target is not None:
        current_user.job_target = user_update.job_target
    if user_update.career_target is not None:
        current_user.career_target = user_update.career_target
    if user_update.academic_level is not None:
        current_user.academic_level = user_update.academic_level    

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user