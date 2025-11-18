from pydantic import BaseModel, Field, validator
from typing import Optional
from security import sanitize_string, sanitize_html_input

class Asistencia(BaseModel):
    IdEmpleado: int = Field(..., gt=0, description="ID del empleado")
    Fecha: str = Field(..., min_length=10, max_length=10, description="Fecha de asistencia (YYYY-MM-DD)")
    HoraEntrada: Optional[str] = Field(None, max_length=5, description="Hora de entrada (HH:mm)")
    HoraSalida: Optional[str] = Field(None, max_length=5, description="Hora de salida (HH:mm)")
    TipoRegistro: str = Field(..., description="Tipo de registro: entrada o salida")
    TipoRegistroOrigen: Optional[str] = Field(default="manual", description="Origen: manual o biometrico")
    Estado: str = Field(default="presente", description="Estado: presente, ausente, tardanza, permiso, vacaciones")
    Observaciones: Optional[str] = Field(None, max_length=500, description="Observaciones adicionales")
    Justificacion: Optional[str] = Field(None, max_length=500, description="Justificación para ausencias o tardanzas")
    HorasTrabajadas: Optional[float] = Field(None, ge=0, description="Horas trabajadas")
    Latitud: Optional[float] = Field(None, description="Latitud GPS")
    Longitud: Optional[float] = Field(None, description="Longitud GPS")
    
    @validator('Fecha')
    def validate_fecha(cls, v):
        v = sanitize_string(v, max_length=10)
        # Validar formato YYYY-MM-DD
        if len(v) != 10 or v[4] != '-' or v[7] != '-':
            raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD')
        return v
    
    @validator('HoraEntrada', 'HoraSalida')
    def validate_hora(cls, v):
        if v is None:
            return None
        v = sanitize_string(v, max_length=5)
        # Validar formato HH:mm
        if len(v) != 5 or v[2] != ':':
            raise ValueError('Formato de hora inválido. Use HH:mm')
        return v
    
    @validator('TipoRegistro')
    def validate_tipo_registro(cls, v):
        v = sanitize_string(v, max_length=20)
        if v not in ['entrada', 'salida']:
            raise ValueError('TipoRegistro debe ser "entrada" o "salida"')
        return v
    
    @validator('TipoRegistroOrigen')
    def validate_tipo_origen(cls, v):
        if v is None:
            return "manual"
        v = sanitize_string(v, max_length=20)
        if v not in ['manual', 'biometrico']:
            raise ValueError('TipoRegistroOrigen debe ser "manual" o "biometrico"')
        return v
    
    @validator('Estado')
    def validate_estado(cls, v):
        v = sanitize_string(v, max_length=20)
        estados_validos = ['presente', 'ausente', 'tardanza', 'permiso', 'vacaciones']
        if v not in estados_validos:
            raise ValueError(f'Estado debe ser uno de: {", ".join(estados_validos)}')
        return v
    
    @validator('Observaciones', 'Justificacion')
    def sanitize_text(cls, v):
        if v is None:
            return None
        return sanitize_html_input(v, max_length=500)
    
    @validator('IdEmpleado')
    def validate_id_empleado(cls, v):
        if v <= 0:
            raise ValueError('ID de empleado debe ser mayor que 0')
        return v

