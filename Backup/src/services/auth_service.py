from fastapi import HTTPException, status
from src.repositories.user_repository import UserRepository
from src.security import verify_password, create_access_token
from src.models.user import UserInDB
from typing import Optional


class AuthService:
    def __init__(self):
        """
        Inicializa el servicio.
        Instancia el UserRepository para acceder a la base de datos.
        """
        self.user_repo = UserRepository()

    def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """
        Verifica si un usuario existe y si la contraseña es correcta.
        
        1. Busca al usuario por email (obteniendo el hash de su contraseña).
        2. Compara la contraseña plana con el hash guardado.
        
        Retorna el objeto UserInDB si la autenticación es exitosa, sino None.
        """
        # El repositorio nos devuelve el modelo UserInDB (que incluye la contraseña)
        user = self.user_repo.find_user_by_email(email)
        
        if not user:
            # Usuario no encontrado
            return None
        
        if not verify_password(password, user.password):
            # Contraseña incorrecta
            return None
            
        # Autenticación exitosa
        return user

    def login_user(self, email: str, password: str) -> dict:
        """
        Orquesta el proceso de login.
        
        1. Autentica al usuario.
        2. Si falla, lanza una excepción HTTP 401 (No autorizado).
        3. Si tiene éxito, crea un token JWT para la sesión del usuario.
        """
        user = self.authenticate_user(email, password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Creamos el token. Guardamos el ID del usuario en el campo 'sub' (subject)
        # El ID debe ser un string (Pydantic ya lo convirtió en UserInDB)
        access_token = create_access_token(data={"sub": user.id})
        
        return {"access_token": access_token, "token_type": "bearer"}