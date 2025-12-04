<<<<<<< HEAD:Backup/src/controllers/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException
# ¡Importante! FastAPI usa OAuth2PasswordRequestForm para el login
# pero depende de 'python-multipart'. Asegúrate de tenerlo en requirements.txt
# Para ser consistentes con tu frontend, usaremos nuestro modelo JSON.
from src.models.auth import LoginRequest, TokenResponse
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Instanciamos el servicio que contiene la lógica
auth_service = AuthService()


@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(form_data: LoginRequest):
    """
    Endpoint para iniciar sesión.
    
    Recibe un JSON con 'email' y 'password'.
    Delega la lógica al 'auth_service'.
    Retorna un TokenResponse (access_token y token_type).
    """
    try:
        # El servicio maneja la autenticación y la creación del token
        token_data = auth_service.login_user(form_data.email, form_data.password)
        return token_data
    except HTTPException as e:
        # Si el servicio lanza un error (ej. 401), lo re-lanzamos
        raise e
    except Exception as e:
        # Captura de errores inesperados
        print(f"Error inesperado en login: {e}")
        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error interno en el servidor."
        )
=======
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..models.user import UserLogin, UserCreate, UserResponse, Token
from ..services.user_service import UserService
from ..repositories.user_repository import UserRepository
from ..config.db import get_database
from ..utils.auth import verify_token, get_credentials_exception

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


async def get_user_service():
    """Dependency to get user service with database connection"""
    database = await get_database()
    user_repository = UserRepository(database)
    return UserService(user_repository)


async def get_current_user_email(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Dependency to get current user email from token"""
    return verify_token(credentials.credentials, get_credentials_exception())


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """Register a new user"""
    try:
        user = await user_service.register_user(user_data)
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    user_service: UserService = Depends(get_user_service)
):
    """Login user and return access token"""
    try:
        token = await user_service.login_user(login_data)
        return token
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user_email: str = Depends(get_current_user_email),
    user_service: UserService = Depends(get_user_service)
):
    """Get current user information"""
    user = await user_service.get_user_by_email(current_user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
>>>>>>> f0a1462d54372cf7b884be9c18e222ee20bf6b6f:src/controllers/auth_controller.py
