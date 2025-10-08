from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    first_name: str = Field(..., alias="nombres")
    last_name: str = Field(..., alias="apellidos")
    email: EmailStr = Field(..., alias="correo")
    password: str = Field(..., alias="contraseña")
    career: str = Field(..., alias="carrera")
    desired_position: str = Field(..., alias="puesto_laboral_deseado")


class UserResponse(BaseModel):
    id: str = Field(..., alias="_id")
    first_name: str = Field(..., alias="nombres")
    last_name: str = Field(..., alias="apellidos")
    email: EmailStr = Field(..., alias="correo")
    career: str = Field(..., alias="carrera")
    desired_position: str = Field(..., alias="puesto_laboral_deseado")

    class Config:
        populate_by_name = True
