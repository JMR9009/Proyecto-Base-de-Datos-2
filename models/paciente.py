"""
Modelo Pydantic para Paciente
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from security import sanitize_string, validate_phone


class Paciente(BaseModel):
    Nombre: str = Field(..., min_length=1, max_length=100)
    Apellido: str = Field(..., min_length=1, max_length=100)
    FechaNacimiento: str = Field(..., min_length=10, max_length=10)
    Genero: str = Field(..., max_length=20)
    Telefono: str = Field(..., min_length=8, max_length=20)
    Email: EmailStr
    Direccion: Optional[str] = Field(None, max_length=255)
    
    @validator('Nombre', 'Apellido', 'Genero')
    def sanitize_text(cls, v):
        return sanitize_string(v, max_length=100)
    
    @validator('Telefono')
    def validate_phone(cls, v):
        v = sanitize_string(v, max_length=20)
        if not validate_phone(v):
            raise ValueError('Formato de teléfono inválido')
        return v
    
    @validator('FechaNacimiento')
    def validate_date(cls, v):
        if len(v) != 10 or v[4] != '-' or v[7] != '-':
            raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD')
        return v
    
    @validator('Direccion')
    def sanitize_address(cls, v):
        if v is None:
            return None
        return sanitize_string(v, max_length=255)


class PacienteResponse(BaseModel):
    IdPaciente: int
    Nombre: str
    Apellido: str
    FechaNacimiento: str
    Genero: str
    Telefono: str
    Email: str
    Direccion: Optional[str] = None
    
    class Config:
        from_attributes = True

