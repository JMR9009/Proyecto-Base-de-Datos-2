"""
Modelo Pydantic para Médico
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from security import sanitize_string, validate_phone


class Medico(BaseModel):
    Nombre: str = Field(..., min_length=1, max_length=100)
    Apellido: str = Field(..., min_length=1, max_length=100)
    Especialidad: str = Field(..., min_length=1, max_length=100)
    Telefono: str = Field(..., min_length=8, max_length=20)
    Email: EmailStr
    
    @validator('Nombre', 'Apellido', 'Especialidad')
    def sanitize_text(cls, v):
        return sanitize_string(v, max_length=100)
    
    @validator('Telefono')
    def validate_phone(cls, v):
        v = sanitize_string(v, max_length=20)
        if not validate_phone(v):
            raise ValueError('Formato de teléfono inválido')
        return v


class MedicoResponse(BaseModel):
    IdMedico: int
    Nombre: str
    Apellido: str
    Especialidad: str
    Telefono: str
    Email: str
    
    class Config:
        from_attributes = True

