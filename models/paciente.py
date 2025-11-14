from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional


class Paciente(BaseModel):
    """Modelo para crear o actualizar un paciente"""
    Nombre: str
    Apellido: str
    FechaNacimiento: date
    Sexo: str
    Telefono: Optional[str] = None
    Direccion: Optional[str] = None
    Email: Optional[EmailStr] = None

    class Config:
        json_schema_extra = {
            "example": {
                "Nombre": "María",
                "Apellido": "González",
                "FechaNacimiento": "1990-05-15",
                "Sexo": "F",
                "Telefono": "0987654321",
                "Direccion": "Calle Principal 123",
                "Email": "maria.gonzalez@email.com"
            }
        }


class PacienteResponse(BaseModel):
    """Modelo para la respuesta de un paciente (incluye el ID)"""
    IdPaciente: int
    Nombre: str
    Apellido: str
    FechaNacimiento: date
    Sexo: str
    Telefono: Optional[str] = None
    Direccion: Optional[str] = None
    Email: Optional[str] = None

    class Config:
        from_attributes = True

