"""
Modelo Pydantic para Asignación de Empleado
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from security import sanitize_string


class AsignacionEmpleado(BaseModel):
    IdEmpleado: int = Field(..., gt=0)
    IdDepartamento: int = Field(..., gt=0)
    IdPuesto: int = Field(..., gt=0)
    FechaAsignacion: Optional[str] = Field(None, max_length=10)
    Estado: str = Field(default="activo", max_length=20)
    
    @validator('FechaAsignacion')
    def validate_date(cls, v):
        if v is None:
            return None
        if len(v) != 10 or v[4] != '-' or v[7] != '-':
            raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD')
        return v


class AsignacionEmpleadoResponse(BaseModel):
    IdAsignacion: int
    IdEmpleado: int
    IdDepartamento: int
    IdPuesto: int
    FechaAsignacion: Optional[str] = None
    Estado: str
    
    class Config:
        from_attributes = True

