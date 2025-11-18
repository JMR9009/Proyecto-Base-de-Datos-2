"""
Modelo Pydantic para Contrato
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from security import sanitize_string


class Contrato(BaseModel):
    IdEmpleado: int = Field(..., gt=0)
    TipoContrato: str = Field(..., max_length=50)  # Permanente, Temporal, Honorarios
    NumeroContrato: Optional[str] = Field(None, max_length=50)
    FechaInicio: str = Field(..., min_length=10, max_length=10)
    FechaFin: Optional[str] = Field(None, min_length=10, max_length=10)
    Salario: float = Field(..., ge=0)
    Moneda: Optional[str] = Field(default="DOP", max_length=10)
    HorasSemana: Optional[int] = Field(None, ge=0, le=168)
    Descripcion: Optional[str] = Field(None, max_length=1000)
    Condiciones: Optional[str] = Field(None, max_length=2000)
    Estado: str = Field(default="vigente", max_length=20)  # vigente, vencido, cancelado, renovado
    FechaFirma: Optional[str] = Field(None, min_length=10, max_length=10)
    DocumentoUrl: Optional[str] = Field(None, max_length=500)
    Observaciones: Optional[str] = Field(None, max_length=1000)
    
    @validator('FechaInicio', 'FechaFin', 'FechaFirma')
    def validate_date(cls, v):
        if v is None:
            return None
        if len(v) != 10 or v[4] != '-' or v[7] != '-':
            raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD')
        return v
    
    @validator('Descripcion', 'Condiciones', 'Observaciones', 'NumeroContrato')
    def sanitize_text(cls, v):
        if v is None:
            return None
        max_len = 2000 if 'Condiciones' in str(cls.__fields__.keys()) else (1000 if 'Descripcion' in str(cls.__fields__.keys()) or 'Observaciones' in str(cls.__fields__.keys()) else 50)
        return sanitize_string(v, max_length=max_len)


class ContratoResponse(BaseModel):
    IdContrato: int
    IdEmpleado: int
    TipoContrato: str
    NumeroContrato: Optional[str] = None
    FechaInicio: str
    FechaFin: Optional[str] = None
    Salario: float
    Moneda: Optional[str] = None
    HorasSemana: Optional[int] = None
    Descripcion: Optional[str] = None
    Condiciones: Optional[str] = None
    Estado: str
    FechaFirma: Optional[str] = None
    DocumentoUrl: Optional[str] = None
    Observaciones: Optional[str] = None
    
    class Config:
        from_attributes = True

