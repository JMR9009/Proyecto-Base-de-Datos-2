"""
Modelo Pydantic para Evaluación de Desempeño
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from security import sanitize_string


class CriterioEvaluado(BaseModel):
    IdCriterio: int = Field(..., gt=0)
    Calificacion: Optional[float] = Field(None, ge=0)
    Comentarios: Optional[str] = Field(None, max_length=500)
    Evidencias: Optional[str] = Field(None, max_length=500)
    
    @validator('Comentarios', 'Evidencias')
    def sanitize_text(cls, v):
        if v is None:
            return None
        return sanitize_string(v, max_length=500)


class EvaluacionDesempeno(BaseModel):
    IdEmpleado: int = Field(..., gt=0)
    IdEvaluador: Optional[int] = Field(None, gt=0)
    TipoEvaluacion: str = Field(..., max_length=50)  # anual, semestral, trimestral, mensual, 360grados, autoevaluacion
    Periodo: str = Field(..., max_length=20)  # 2024-Q1, 2024-S1, 2024, etc.
    FechaEvaluacion: str = Field(..., min_length=10, max_length=10)
    FechaInicioPeriodo: Optional[str] = Field(None, min_length=10, max_length=10)
    FechaFinPeriodo: Optional[str] = Field(None, min_length=10, max_length=10)
    Estado: str = Field(default="programada", max_length=20)  # programada, en_proceso, completada, cancelada
    CalificacionFinal: Optional[float] = Field(None, ge=0)
    Fortalezas: Optional[str] = Field(None, max_length=1000)
    AreasMejora: Optional[str] = Field(None, max_length=1000)
    ComentariosEvaluador: Optional[str] = Field(None, max_length=1000)
    ComentariosEmpleado: Optional[str] = Field(None, max_length=1000)
    PlanDesarrollo: Optional[str] = Field(None, max_length=1000)
    FirmaEvaluador: Optional[str] = Field(None, max_length=500)
    FirmaEmpleado: Optional[str] = Field(None, max_length=500)
    FechaFirmaEvaluador: Optional[str] = Field(None, min_length=10, max_length=10)
    FechaFirmaEmpleado: Optional[str] = Field(None, min_length=10, max_length=10)
    CriteriosEvaluados: Optional[List[CriterioEvaluado]] = None
    
    @validator('FechaEvaluacion', 'FechaInicioPeriodo', 'FechaFinPeriodo', 'FechaFirmaEvaluador', 'FechaFirmaEmpleado')
    def validate_date(cls, v):
        if v is None:
            return None
        if len(v) != 10 or v[4] != '-' or v[7] != '-':
            raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD')
        return v
    
    @validator('Fortalezas', 'AreasMejora', 'ComentariosEvaluador', 'ComentariosEmpleado', 'PlanDesarrollo')
    def sanitize_text(cls, v):
        if v is None:
            return None
        return sanitize_string(v, max_length=1000)


class EvaluacionDesempenoResponse(BaseModel):
    IdEvaluacion: int
    IdEmpleado: int
    IdEvaluador: Optional[int] = None
    TipoEvaluacion: str
    Periodo: str
    FechaEvaluacion: str
    FechaInicioPeriodo: Optional[str] = None
    FechaFinPeriodo: Optional[str] = None
    Estado: str
    CalificacionFinal: Optional[float] = None
    Fortalezas: Optional[str] = None
    AreasMejora: Optional[str] = None
    ComentariosEvaluador: Optional[str] = None
    ComentariosEmpleado: Optional[str] = None
    PlanDesarrollo: Optional[str] = None
    FirmaEvaluador: Optional[str] = None
    FirmaEmpleado: Optional[str] = None
    FechaFirmaEvaluador: Optional[str] = None
    FechaFirmaEmpleado: Optional[str] = None
    
    class Config:
        from_attributes = True


class CriterioEvaluacion(BaseModel):
    Nombre: str = Field(..., min_length=1, max_length=100)
    Descripcion: Optional[str] = Field(None, max_length=500)
    Peso: Optional[float] = Field(None, ge=0, le=100)  # porcentaje del total
    TipoEscala: str = Field(..., max_length=50)  # numerica, porcentual, cualitativa
    EscalaMinima: Optional[float] = Field(None, ge=0)
    EscalaMaxima: Optional[float] = Field(None, ge=0)
    Activo: Optional[bool] = Field(default=True)
    
    @validator('Nombre', 'Descripcion')
    def sanitize_text(cls, v):
        if v is None:
            return None
        max_len = 500 if 'Descripcion' in str(cls.__fields__.keys()) else 100
        return sanitize_string(v, max_length=max_len)


class CriterioEvaluacionResponse(BaseModel):
    IdCriterio: int
    Nombre: str
    Descripcion: Optional[str] = None
    Peso: Optional[float] = None
    TipoEscala: str
    EscalaMinima: Optional[float] = None
    EscalaMaxima: Optional[float] = None
    Activo: Optional[bool] = None
    
    class Config:
        from_attributes = True

