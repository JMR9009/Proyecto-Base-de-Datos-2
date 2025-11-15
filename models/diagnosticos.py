from pydantic import BaseModel
from datetime import date
from typing import Optional


class Diagnostico(BaseModel):
    """Modelo para crear o actualizar un diagnóstico"""
    IdPaciente: int
    Descripcion: str
    FechaDiagnostico: date
    CodigoICD10: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "IdPaciente": 1,
                "Descripcion": "Hipertensión arterial",
                "FechaDiagnostico": "2024-01-15",
                "CodigoICD10": "I10"
            }
        }


class DiagnosticoResponse(BaseModel):
    """Modelo para la respuesta de un diagnóstico (incluye el ID)"""
    IdDiagnostico: int
    IdPaciente: int
    Descripcion: str
    FechaDiagnostico: date
    CodigoICD10: Optional[str] = None

    class Config:
        from_attributes = True


class Tratamiento(BaseModel):
    """Modelo para crear o actualizar un tratamiento"""
    IdDiagnostico: int
    Descripcion: str
    FechaInicio: date
    FechaFin: Optional[date] = None
    Medicamentos: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "IdDiagnostico": 1,
                "Descripcion": "Antihipertensivo oral",
                "FechaInicio": "2024-01-15",
                "FechaFin": "2024-06-15",
                "Medicamentos": "Losartán 50mg diarios"
            }
        }


class TratamientoResponse(BaseModel):
    """Modelo para la respuesta de un tratamiento (incluye el ID)"""
    IdTratamiento: int
    IdDiagnostico: int
    Descripcion: str
    FechaInicio: date
    FechaFin: Optional[date] = None
    Medicamentos: Optional[str] = None

    class Config:
        from_attributes = True
