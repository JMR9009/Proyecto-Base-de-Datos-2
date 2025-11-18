"""
Modelo Pydantic para Departamento
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from security import sanitize_string, validate_phone


class Departamento(BaseModel):
    Nombre: str = Field(..., min_length=1, max_length=100)
    Descripcion: Optional[str] = Field(None, max_length=500)
    Responsable: Optional[str] = Field(None, max_length=100)
    Telefono: Optional[str] = Field(None, max_length=20)
    Email: Optional[EmailStr] = None
    Estado: str = Field(default="activo", max_length=20)
    
    @validator('Nombre', 'Descripcion', 'Responsable')
    def sanitize_text(cls, v):
        if v is None:
            return None
        return sanitize_string(v, max_length=500 if 'Descripcion' in str(cls.__fields__.keys()) else 100)
    
    @validator('Telefono')
    def validate_phone(cls, v):
        if v is None:
            return None
        v = sanitize_string(v, max_length=20)
        if not validate_phone(v):
            raise ValueError('Formato de teléfono inválido')
        return v


class DepartamentoResponse(BaseModel):
    IdDepartamento: int
    Nombre: str
    Descripcion: Optional[str] = None
    Responsable: Optional[str] = None
    Telefono: Optional[str] = None
    Email: Optional[str] = None
    Estado: str
    
    class Config:
        from_attributes = True

