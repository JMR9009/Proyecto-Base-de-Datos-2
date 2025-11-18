"""
Modelo Pydantic para Puesto
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from security import sanitize_string


class Puesto(BaseModel):
    Nombre: str = Field(..., min_length=1, max_length=100)
    IdDepartamento: int = Field(..., gt=0)
    Nivel: Optional[str] = Field(None, max_length=50)
    Descripcion: Optional[str] = Field(None, max_length=500)
    SalarioMinimo: Optional[float] = Field(None, ge=0)
    SalarioMaximo: Optional[float] = Field(None, ge=0)
    Requisitos: Optional[str] = Field(None, max_length=1000)
    Estado: str = Field(default="activo", max_length=20)
    
    @validator('Nombre', 'Nivel', 'Descripcion', 'Requisitos')
    def sanitize_text(cls, v):
        if v is None:
            return None
        max_len = 1000 if 'Requisitos' in str(cls.__fields__.keys()) else (500 if 'Descripcion' in str(cls.__fields__.keys()) else 100)
        return sanitize_string(v, max_length=max_len)
    
    @validator('SalarioMaximo')
    def validate_salary_range(cls, v, values):
        if v is not None and 'SalarioMinimo' in values and values['SalarioMinimo'] is not None:
            if v < values['SalarioMinimo']:
                raise ValueError('El salario máximo debe ser mayor o igual al salario mínimo')
        return v


class PuestoResponse(BaseModel):
    IdPuesto: int
    Nombre: str
    IdDepartamento: int
    Nivel: Optional[str] = None
    Descripcion: Optional[str] = None
    SalarioMinimo: Optional[float] = None
    SalarioMaximo: Optional[float] = None
    Requisitos: Optional[str] = None
    Estado: str
    
    class Config:
        from_attributes = True

