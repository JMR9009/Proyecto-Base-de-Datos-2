from pydantic import BaseModel, Field, validator
from security import sanitize_string, sanitize_html_input

class Cita(BaseModel):
    IdPaciente: int = Field(..., gt=0, description="ID del paciente")
    IdMedico: int = Field(..., gt=0, description="ID del médico")
    FechaHora: str = Field(..., min_length=10, max_length=50, description="Fecha y hora de la cita")
    Motivo: str = Field(..., min_length=1, max_length=500, description="Motivo de la cita")
    Estado: str = Field(default="Programada", max_length=50)
    
    @validator('Motivo')
    def sanitize_motivo(cls, v):
        # Sanitizar y escapar HTML para prevenir XSS si se muestra en frontend
        return sanitize_html_input(v, max_length=500)
    
    @validator('Estado')
    def sanitize_estado(cls, v):
        # Sanitizar y escapar HTML para prevenir XSS
        return sanitize_html_input(v, max_length=50)
    
    @validator('IdPaciente', 'IdMedico')
    def validate_ids(cls, v):
        if v <= 0:
            raise ValueError('ID debe ser mayor que 0')
        return v

