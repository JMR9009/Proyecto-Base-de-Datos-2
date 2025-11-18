"""
Modelo Pydantic para Vacaciones y Permisos
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from security import sanitize_string


class SolicitudVacacion(BaseModel):
    IdEmpleado: int = Field(..., gt=0)
    FechaInicio: str = Field(..., min_length=10, max_length=10)
    FechaFin: str = Field(..., min_length=10, max_length=10)
    DiasSolicitados: int = Field(..., gt=0)
    Motivo: Optional[str] = Field(None, max_length=500)
    Estado: str = Field(default="pendiente", max_length=20)  # pendiente, aprobada, rechazada, cancelada
    IdAprobador: Optional[int] = Field(None, gt=0)
    FechaAprobacion: Optional[str] = Field(None, min_length=10, max_length=10)
    ComentariosAprobador: Optional[str] = Field(None, max_length=500)
    
    @validator('FechaInicio', 'FechaFin', 'FechaAprobacion')
    def validate_date(cls, v):
        if v is None:
            return None
        if len(v) != 10 or v[4] != '-' or v[7] != '-':
            raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD')
        return v
    
    @validator('Motivo', 'ComentariosAprobador')
    def sanitize_text(cls, v):
        if v is None:
            return None
        return sanitize_string(v, max_length=500)


class SolicitudVacacionResponse(BaseModel):
    IdSolicitudVacacion: int
    IdEmpleado: int
    FechaInicio: str
    FechaFin: str
    DiasSolicitados: int
    Motivo: Optional[str] = None
    Estado: str
    IdAprobador: Optional[int] = None
    FechaAprobacion: Optional[str] = None
    ComentariosAprobador: Optional[str] = None
    FechaCreacion: Optional[str] = None
    FechaActualizacion: Optional[str] = None
    
    class Config:
        from_attributes = True


class SolicitudPermiso(BaseModel):
    IdEmpleado: int = Field(..., gt=0)
    TipoPermiso: str = Field(..., max_length=50)  # personal, medico, familiar, otros
    FechaInicio: str = Field(..., min_length=10, max_length=10)
    FechaFin: Optional[str] = Field(None, min_length=10, max_length=10)
    HorasSolicitadas: Optional[int] = Field(None, ge=0)
    DiasSolicitados: Optional[int] = Field(None, ge=0)
    Motivo: str = Field(..., min_length=1, max_length=500)
    Estado: str = Field(default="pendiente", max_length=20)  # pendiente, aprobada, rechazada, cancelada
    IdAprobador: Optional[int] = Field(None, gt=0)
    FechaAprobacion: Optional[str] = Field(None, min_length=10, max_length=10)
    ComentariosAprobador: Optional[str] = Field(None, max_length=500)
    
    @validator('FechaInicio', 'FechaFin', 'FechaAprobacion')
    def validate_date(cls, v):
        if v is None:
            return None
        if len(v) != 10 or v[4] != '-' or v[7] != '-':
            raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD')
        return v
    
    @validator('Motivo', 'ComentariosAprobador')
    def sanitize_text(cls, v):
        if v is None:
            return None
        return sanitize_string(v, max_length=500)


class SolicitudPermisoResponse(BaseModel):
    IdSolicitudPermiso: int
    IdEmpleado: int
    TipoPermiso: str
    FechaInicio: str
    FechaFin: Optional[str] = None
    HorasSolicitadas: Optional[int] = None
    DiasSolicitados: Optional[int] = None
    Motivo: str
    Estado: str
    IdAprobador: Optional[int] = None
    FechaAprobacion: Optional[str] = None
    ComentariosAprobador: Optional[str] = None
    FechaCreacion: Optional[str] = None
    FechaActualizacion: Optional[str] = None
    
    class Config:
        from_attributes = True


class BalanceVacaciones(BaseModel):
    IdEmpleado: int = Field(..., gt=0)
    Periodo: str = Field(..., max_length=20)  # 2024
    DiasAsignados: int = Field(..., ge=0)
    DiasTomados: int = Field(default=0, ge=0)
    DiasPendientes: int = Field(default=0, ge=0)
    DiasDisponibles: int = Field(default=0, ge=0)
    DiasVencidos: Optional[int] = Field(None, ge=0)
    FechaVencimiento: Optional[str] = Field(None, min_length=10, max_length=10)
    
    @validator('FechaVencimiento')
    def validate_date(cls, v):
        if v is None:
            return None
        if len(v) != 10 or v[4] != '-' or v[7] != '-':
            raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD')
        return v


class BalanceVacacionesResponse(BaseModel):
    IdBalance: int
    IdEmpleado: int
    Periodo: str
    DiasAsignados: int
    DiasTomados: int
    DiasPendientes: int
    DiasDisponibles: int
    DiasVencidos: Optional[int] = None
    FechaVencimiento: Optional[str] = None
    
    class Config:
        from_attributes = True

