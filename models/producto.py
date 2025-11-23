from pydantic import BaseModel, condecimal, Field
from typing import Optional
from decimal import Decimal

PrecioType = condecimal(max_digits=10, decimal_places=2)

class Producto(BaseModel):
    """Modelo para crear o actualizar un producto"""
    Nombre: str
    Descripcion: Optional[str] = None
    Stock: int = 0
    Precio: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
   


    class Config:
        json_schema_extra = {
            "example": {
                "Nombre": "Paracetamol 500mg",
                "Descripcion": "Caja con 20 tabletas",
                "Stock": 10,
                "Precio": 50.00
            }
        }

class ProductoResponse(BaseModel):
    """Modelo para la respuesta de un producto (incluye el ID)"""
    ID: int
    Nombre: str
    Descripcion: Optional[str] = None
    Stock: int
    Precio: float

    class Config:
        from_attributes = True

class ProductoUpdateStock(BaseModel):
    """Modelo para actualizar solo el stock de un producto"""
    Stock: int

    class Config:
        json_schema_extra = {
            "example": {
                "Stock": 15
            }
        }