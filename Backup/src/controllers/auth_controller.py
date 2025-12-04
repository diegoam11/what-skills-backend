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