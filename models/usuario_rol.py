"""
Modelo Pydantic para Usuarios y Roles
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from security import sanitize_string, validate_phone


class Rol(BaseModel):
    Nombre: str = Field(..., min_length=1, max_length=100)
    Descripcion: Optional[str] = Field(None, max_length=500)
    Permisos: Optional[List[str]] = None
    Activo: bool = Field(default=True)
    
    @validator('Nombre', 'Descripcion')
    def sanitize_text(cls, v):
        if v is None:
            return None
        max_len = 500 if 'Descripcion' in str(cls.__fields__.keys()) else 100
        return sanitize_string(v, max_length=max_len)


class RolResponse(BaseModel):
    IdRol: int
    Nombre: str
    Descripcion: Optional[str] = None
    Activo: bool
    FechaCreacion: Optional[str] = None
    FechaActualizacion: Optional[str] = None
    
    class Config:
        from_attributes = True


class Usuario(BaseModel):
    NombreUsuario: str = Field(..., min_length=3, max_length=50)
    Email: EmailStr
    Nombre: str = Field(..., min_length=1, max_length=100)
    Apellido: str = Field(..., min_length=1, max_length=100)
    Telefono: Optional[str] = Field(None, max_length=20)
    IdRol: Optional[int] = Field(None, gt=0)
    IdEmpleado: Optional[int] = Field(None, gt=0)
    Estado: str = Field(default="activo", max_length=20)  # activo, inactivo, bloqueado
    Password: Optional[str] = Field(None, min_length=6)  # Solo para creación/actualización
    
    @validator('NombreUsuario', 'Nombre', 'Apellido')
    def sanitize_text(cls, v):
        return sanitize_string(v, max_length=100)
    
    @validator('Telefono')
    def validate_phone(cls, v):
        if v is None:
            return None
        v = sanitize_string(v, max_length=20)
        if not validate_phone(v):
            raise ValueError('Formato de teléfono inválido')
        return v


class UsuarioResponse(BaseModel):
    IdUsuario: int
    NombreUsuario: str
    Email: str
    Nombre: Optional[str] = None
    Apellido: Optional[str] = None
    Telefono: Optional[str] = None
    IdRol: Optional[int] = None
    IdEmpleado: Optional[int] = None
    Estado: str
    UltimoAcceso: Optional[str] = None
    FechaCreacion: Optional[str] = None
    FechaActualizacion: Optional[str] = None
    IntentosFallidos: Optional[int] = None
    FechaBloqueo: Optional[str] = None
    
    class Config:
        from_attributes = True


class Permiso(BaseModel):
    Nombre: str = Field(..., min_length=1, max_length=100)
    Descripcion: Optional[str] = Field(None, max_length=500)
    Modulo: str = Field(..., max_length=50)
    Accion: str = Field(..., max_length=50)
    Activo: bool = Field(default=True)
    
    @validator('Nombre', 'Descripcion')
    def sanitize_text(cls, v):
        if v is None:
            return None
        max_len = 500 if 'Descripcion' in str(cls.__fields__.keys()) else 100
        return sanitize_string(v, max_length=max_len)


class PermisoResponse(BaseModel):
    IdPermiso: int
    Nombre: str
    Descripcion: Optional[str] = None
    Modulo: str
    Accion: str
    Activo: bool
    
    class Config:
        from_attributes = True


class HistorialUsuario(BaseModel):
    IdUsuario: int = Field(..., gt=0)
    Accion: str = Field(..., max_length=50)  # login, logout, cambio_password, cambio_rol, bloqueado, desbloqueado
    IpAddress: Optional[str] = Field(None, max_length=50)
    UserAgent: Optional[str] = Field(None, max_length=500)
    Detalles: Optional[str] = Field(None, max_length=1000)
    
    @validator('Detalles')
    def sanitize_text(cls, v):
        if v is None:
            return None
        return sanitize_string(v, max_length=1000)


class HistorialUsuarioResponse(BaseModel):
    IdHistorial: int
    IdUsuario: int
    Accion: str
    IpAddress: Optional[str] = None
    UserAgent: Optional[str] = None
    FechaAccion: Optional[str] = None
    Detalles: Optional[str] = None
    
    class Config:
        from_attributes = True

