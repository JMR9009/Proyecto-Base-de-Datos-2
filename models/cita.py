from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Cita(BaseModel):
    """Modelo para crear una nueva cita"""
    IdPaciente: int
    IdMedico: int
    FechaCita: datetime
    Motivo: str
    Estado: str

    class Config:
        json_schema_extra = {
            "example": {
                "IdPaciente": 1,
                "IdMedico": 1,
                "FechaCita": "2024-01-15T10:00:00",
                "Motivo": "Consulta general",
                "Estado": "Programada"
            }
        }


class CitaResponse(BaseModel):
    """Modelo para la respuesta de una cita (incluye el ID)"""
    IdCita: int
    IdPaciente: int
    IdMedico: int
    FechaCita: datetime
    Motivo: str
    Estado: str

    class Config:
        from_attributes = True

