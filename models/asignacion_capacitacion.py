"""
Modelo Pydantic para Asignación de Capacitación
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from security import sanitize_string


class Evaluacion(BaseModel):
    TipoEvaluacion: str = Field(..., max_length=50)  # examen, practica, proyecto, participacion
    Preguntas: Optional[int] = Field(None, ge=0)
    RespuestasCorrectas: Optional[int] = Field(None, ge=0)
    PuntosObtenidos: Optional[float] = Field(None, ge=0)
    PuntosTotales: Optional[float] = Field(None, ge=0)
    FechaEvaluacion: str = Field(..., min_length=10, max_length=10)
    Observaciones: Optional[str] = Field(None, max_length=500)
    
    @validator('FechaEvaluacion')
    def validate_date(cls, v):
        if len(v) != 10 or v[4] != '-' or v[7] != '-':
            raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD')
        return v


class AsignacionCapacitacion(BaseModel):
    IdCapacitacion: int = Field(..., gt=0)
    IdEmpleado: int = Field(..., gt=0)
    FechaAsignacion: str = Field(..., min_length=10, max_length=10)
    Estado: str = Field(default="asignada", max_length=20)  # asignada, en_progreso, completada, cancelada, no_asistio
    Calificacion: Optional[float] = Field(None, ge=0, le=100)
    Asistencia: Optional[float] = Field(None, ge=0, le=100)
    Observaciones: Optional[str] = Field(None, max_length=1000)
    CertificadoUrl: Optional[str] = Field(None, max_length=500)
    FechaCompletacion: Optional[str] = Field(None, min_length=10, max_length=10)
    FechaEmisionCertificado: Optional[str] = Field(None, min_length=10, max_length=10)
    NumeroCertificado: Optional[str] = Field(None, max_length=50)
    
    @validator('FechaAsignacion', 'FechaCompletacion', 'FechaEmisionCertificado')
    def validate_date(cls, v):
        if v is None:
            return None
        if len(v) != 10 or v[4] != '-' or v[7] != '-':
            raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD')
        return v
    
    @validator('Observaciones')
    def sanitize_text(cls, v):
        if v is None:
            return None
        return sanitize_string(v, max_length=1000)


class AsignacionCapacitacionResponse(BaseModel):
    IdAsignacion: int
    IdCapacitacion: int
    IdEmpleado: int
    FechaAsignacion: str
    Estado: str
    Calificacion: Optional[float] = None
    Asistencia: Optional[float] = None
    Observaciones: Optional[str] = None
    CertificadoUrl: Optional[str] = None
    FechaCompletacion: Optional[str] = None
    FechaEmisionCertificado: Optional[str] = None
    NumeroCertificado: Optional[str] = None
    
    class Config:
        from_attributes = True

