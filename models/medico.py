from pydantic import BaseModel, EmailStr
from typing import Optional


class Medico(BaseModel):
    """Modelo para crear o actualizar un médico"""
    Nombre: str
    Apellido: str
    Especialidad: str
    Telefono: str
    Email: EmailStr

    class Config:
        json_schema_extra = {
            "example": {
                "Nombre": "Juan",
                "Apellido": "Pérez",
                "Especialidad": "Cardiología",
                "Telefono": "1234567890",
                "Email": "juan.perez@clinica.com"
            }
        }


class MedicoResponse(BaseModel):
    """Modelo para la respuesta de un médico (incluye el ID)"""
    IdMedico: int
    Nombre: str
    Apellido: str
    Especialidad: str
    Telefono: str
    Email: str

    class Config:
        from_attributes = True

