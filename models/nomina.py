"""
Modelo Pydantic para Nómina
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from security import sanitize_string


class ConceptoNomina(BaseModel):
    Nombre: str = Field(..., min_length=1, max_length=100)
    Descripcion: Optional[str] = Field(None, max_length=500)
    Tipo: str = Field(..., max_length=20)  # deduccion, bonificacion
    TipoCalculo: str = Field(..., max_length=20)  # fijo, porcentual
    Valor: float = Field(..., ge=0)
    AplicaA: str = Field(..., max_length=20)  # todos, departamento, puesto, empleado
    IdDepartamento: Optional[int] = Field(None, gt=0)
    IdPuesto: Optional[int] = Field(None, gt=0)
    IdEmpleado: Optional[int] = Field(None, gt=0)
    Activo: bool = Field(default=True)
    Orden: Optional[int] = Field(None, ge=0)
    
    @validator('Nombre', 'Descripcion')
    def sanitize_text(cls, v):
        if v is None:
            return None
        max_len = 500 if 'Descripcion' in str(cls.__fields__.keys()) else 100
        return sanitize_string(v, max_length=max_len)


class ConceptoNominaResponse(BaseModel):
    IdConcepto: int
    Nombre: str
    Descripcion: Optional[str] = None
    Tipo: str
    TipoCalculo: str
    Valor: float
    AplicaA: str
    IdDepartamento: Optional[int] = None
    IdPuesto: Optional[int] = None
    IdEmpleado: Optional[int] = None
    Activo: bool
    Orden: Optional[int] = None
    
    class Config:
        from_attributes = True


class DetalleNomina(BaseModel):
    IdNomina: int = Field(..., gt=0)
    IdEmpleado: int = Field(..., gt=0)
    SalarioBase: float = Field(..., ge=0)
    HorasTrabajadas: Optional[float] = Field(None, ge=0)
    HorasExtras: Optional[float] = Field(None, ge=0)
    Bonificaciones: float = Field(default=0, ge=0)
    Deducciones: float = Field(default=0, ge=0)
    TotalDevengado: float = Field(default=0, ge=0)
    TotalDeducido: float = Field(default=0, ge=0)
    NetoAPagar: float = Field(default=0, ge=0)
    Observaciones: Optional[str] = Field(None, max_length=500)
    
    @validator('Observaciones')
    def sanitize_text(cls, v):
        if v is None:
            return None
        return sanitize_string(v, max_length=500)


class DetalleNominaResponse(BaseModel):
    IdDetalleNomina: int
    IdNomina: int
    IdEmpleado: int
    SalarioBase: float
    HorasTrabajadas: Optional[float] = None
    HorasExtras: Optional[float] = None
    Bonificaciones: float
    Deducciones: float
    TotalDevengado: float
    TotalDeducido: float
    NetoAPagar: float
    Observaciones: Optional[str] = None
    
    class Config:
        from_attributes = True


class Nomina(BaseModel):
    Periodo: str = Field(..., max_length=20)  # 2024-01, 2024-Q1, etc.
    FechaInicio: str = Field(..., min_length=10, max_length=10)
    FechaFin: str = Field(..., min_length=10, max_length=10)
    FechaPago: str = Field(..., min_length=10, max_length=10)
    TipoNomina: str = Field(..., max_length=20)  # quincenal, mensual, extraordinaria
    Estado: str = Field(default="borrador", max_length=20)  # borrador, calculada, pagada, cancelada
    TotalEmpleados: int = Field(default=0, ge=0)
    TotalDevengado: float = Field(default=0, ge=0)
    TotalDeducido: float = Field(default=0, ge=0)
    TotalNeto: float = Field(default=0, ge=0)
    Observaciones: Optional[str] = Field(None, max_length=1000)
    
    @validator('FechaInicio', 'FechaFin', 'FechaPago')
    def validate_date(cls, v):
        if len(v) != 10 or v[4] != '-' or v[7] != '-':
            raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD')
        return v
    
    @validator('Observaciones')
    def sanitize_text(cls, v):
        if v is None:
            return None
        return sanitize_string(v, max_length=1000)


class NominaResponse(BaseModel):
    IdNomina: int
    Periodo: str
    FechaInicio: str
    FechaFin: str
    FechaPago: str
    TipoNomina: str
    Estado: str
    TotalEmpleados: int
    TotalDevengado: float
    TotalDeducido: float
    TotalNeto: float
    Observaciones: Optional[str] = None
    FechaCreacion: Optional[str] = None
    FechaActualizacion: Optional[str] = None
    
    class Config:
        from_attributes = True

