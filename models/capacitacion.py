"""
Modelo Pydantic para Capacitación
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from security import sanitize_string


class Capacitacion(BaseModel):
    Nombre: str = Field(..., min_length=1, max_length=200)
    Descripcion: Optional[str] = Field(None, max_length=1000)
    Tipo: str = Field(..., max_length=50)  # curso, taller, seminario, conferencia, certificacion
    Modalidad: str = Field(..., max_length=50)  # presencial, virtual, mixta
    DuracionHoras: Optional[int] = Field(None, ge=0)
    FechaInicio: str = Field(..., min_length=10, max_length=10)
    FechaFin: Optional[str] = Field(None, min_length=10, max_length=10)
    Instructor: Optional[str] = Field(None, max_length=100)
    Lugar: Optional[str] = Field(None, max_length=200)
    Costo: Optional[float] = Field(None, ge=0)
    Estado: str = Field(default="programada", max_length=20)  # programada, en_curso, completada, cancelada
    CapacidadMaxima: Optional[int] = Field(None, ge=0)
    Requisitos: Optional[str] = Field(None, max_length=1000)
    Objetivos: Optional[str] = Field(None, max_length=1000)
    Certificado: Optional[bool] = Field(default=False)
    
    @validator('FechaInicio', 'FechaFin')
    def validate_date(cls, v):
        if v is None:
            return None
        if len(v) != 10 or v[4] != '-' or v[7] != '-':
            raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD')
        return v
    
    @validator('Nombre', 'Descripcion', 'Instructor', 'Lugar', 'Requisitos', 'Objetivos')
    def sanitize_text(cls, v):
        if v is None:
            return None
        max_len = 1000 if 'Descripcion' in str(cls.__fields__.keys()) or 'Requisitos' in str(cls.__fields__.keys()) or 'Objetivos' in str(cls.__fields__.keys()) else (200 if 'Lugar' in str(cls.__fields__.keys()) else 100)
        return sanitize_string(v, max_length=max_len)


class CapacitacionResponse(BaseModel):
    IdCapacitacion: int
    Nombre: str
    Descripcion: Optional[str] = None
    Tipo: str
    Modalidad: str
    DuracionHoras: Optional[int] = None
    FechaInicio: str
    FechaFin: Optional[str] = None
    Instructor: Optional[str] = None
    Lugar: Optional[str] = None
    Costo: Optional[float] = None
    Estado: str
    CapacidadMaxima: Optional[int] = None
    Requisitos: Optional[str] = None
    Objetivos: Optional[str] = None
    Certificado: Optional[bool] = None
    
    class Config:
        from_attributes = True

