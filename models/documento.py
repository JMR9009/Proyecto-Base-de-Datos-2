"""
Modelo Pydantic para Documentación
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from security import sanitize_string


class Documento(BaseModel):
    Titulo: str = Field(..., min_length=1, max_length=200)
    Descripcion: Optional[str] = Field(None, max_length=1000)
    Categoria: str = Field(..., max_length=100)
    TipoDocumento: str = Field(..., max_length=50)  # manual, politica, procedimiento, formulario, contrato, otro
    Version: str = Field(..., max_length=20)
    ArchivoUrl: Optional[str] = Field(None, max_length=500)
    ArchivoNombre: Optional[str] = Field(None, max_length=200)
    TamañoArchivo: Optional[int] = Field(None, ge=0)
    Estado: str = Field(default="borrador", max_length=20)  # borrador, publicado, archivado, eliminado
    Visibilidad: str = Field(default="publico", max_length=20)  # publico, privado, restringido
    Tags: Optional[List[str]] = None
    IdCreador: Optional[int] = Field(None, gt=0)
    IdDepartamento: Optional[int] = Field(None, gt=0)
    FechaPublicacion: Optional[str] = Field(None, min_length=10, max_length=10)
    FechaVencimiento: Optional[str] = Field(None, min_length=10, max_length=10)
    Observaciones: Optional[str] = Field(None, max_length=1000)
    
    @validator('FechaPublicacion', 'FechaVencimiento')
    def validate_date(cls, v):
        if v is None:
            return None
        if len(v) != 10 or v[4] != '-' or v[7] != '-':
            raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD')
        return v
    
    @validator('Titulo', 'Descripcion', 'Observaciones')
    def sanitize_text(cls, v):
        if v is None:
            return None
        max_len = 1000 if 'Descripcion' in str(cls.__fields__.keys()) or 'Observaciones' in str(cls.__fields__.keys()) else 200
        return sanitize_string(v, max_length=max_len)


class DocumentoResponse(BaseModel):
    IdDocumento: int
    Titulo: str
    Descripcion: Optional[str] = None
    Categoria: str
    TipoDocumento: str
    Version: str
    ArchivoUrl: Optional[str] = None
    ArchivoNombre: Optional[str] = None
    TamañoArchivo: Optional[int] = None
    Estado: str
    Visibilidad: str
    IdCreador: Optional[int] = None
    IdDepartamento: Optional[int] = None
    FechaCreacion: Optional[str] = None
    FechaActualizacion: Optional[str] = None
    FechaPublicacion: Optional[str] = None
    FechaVencimiento: Optional[str] = None
    Observaciones: Optional[str] = None
    
    class Config:
        from_attributes = True


class VersionDocumento(BaseModel):
    IdDocumento: int = Field(..., gt=0)
    Version: str = Field(..., max_length=20)
    Cambios: Optional[str] = Field(None, max_length=1000)
    ArchivoUrl: Optional[str] = Field(None, max_length=500)
    ArchivoNombre: Optional[str] = Field(None, max_length=200)
    TamañoArchivo: Optional[int] = Field(None, ge=0)
    IdCreador: Optional[int] = Field(None, gt=0)
    EsVersionActual: bool = Field(default=True)
    
    @validator('Cambios')
    def sanitize_text(cls, v):
        if v is None:
            return None
        return sanitize_string(v, max_length=1000)


class VersionDocumentoResponse(BaseModel):
    IdVersion: int
    IdDocumento: int
    Version: str
    Cambios: Optional[str] = None
    ArchivoUrl: Optional[str] = None
    ArchivoNombre: Optional[str] = None
    TamañoArchivo: Optional[int] = None
    IdCreador: Optional[int] = None
    FechaCreacion: Optional[str] = None
    EsVersionActual: bool
    
    class Config:
        from_attributes = True


class CategoriaDocumento(BaseModel):
    Nombre: str = Field(..., min_length=1, max_length=100)
    Descripcion: Optional[str] = Field(None, max_length=500)
    Icono: Optional[str] = Field(None, max_length=50)
    Color: Optional[str] = Field(None, max_length=20)
    Orden: Optional[int] = Field(None, ge=0)
    Activa: bool = Field(default=True)
    
    @validator('Nombre', 'Descripcion')
    def sanitize_text(cls, v):
        if v is None:
            return None
        max_len = 500 if 'Descripcion' in str(cls.__fields__.keys()) else 100
        return sanitize_string(v, max_length=max_len)


class CategoriaDocumentoResponse(BaseModel):
    IdCategoria: int
    Nombre: str
    Descripcion: Optional[str] = None
    Icono: Optional[str] = None
    Color: Optional[str] = None
    Orden: Optional[int] = None
    Activa: bool
    
    class Config:
        from_attributes = True


class HistorialDocumento(BaseModel):
    IdDocumento: int = Field(..., gt=0)
    Accion: str = Field(..., max_length=50)  # creado, actualizado, eliminado, publicado, archivado, descargado, visualizado
    IdUsuario: Optional[int] = Field(None, gt=0)
    Comentarios: Optional[str] = Field(None, max_length=500)
    
    @validator('Comentarios')
    def sanitize_text(cls, v):
        if v is None:
            return None
        return sanitize_string(v, max_length=500)


class HistorialDocumentoResponse(BaseModel):
    IdHistorial: int
    IdDocumento: int
    Accion: str
    IdUsuario: Optional[int] = None
    Comentarios: Optional[str] = None
    FechaAccion: Optional[str] = None
    
    class Config:
        from_attributes = True

