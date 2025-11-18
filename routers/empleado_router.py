from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List
from database import get_db_connection
from security import sanitize_string, validate_phone, safe_error_message
from auth import get_current_active_user
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/empleados", tags=["empleados"])


class Empleado(BaseModel):
    Nombre: str = Field(..., min_length=1, max_length=100)
    Apellido: str = Field(..., min_length=1, max_length=100)
    FechaNacimiento: Optional[str] = Field(None, max_length=10)
    Genero: Optional[str] = Field(None, max_length=20)
    Telefono: str = Field(..., min_length=8, max_length=20)
    Email: EmailStr
    Direccion: Optional[str] = Field(None, max_length=255)
    Cedula: Optional[str] = Field(None, max_length=20)
    Cargo: str = Field(..., min_length=1, max_length=100)
    Departamento: str = Field(..., min_length=1, max_length=100)
    FechaContratacion: str = Field(..., min_length=10, max_length=10)
    Salario: Optional[float] = Field(None, ge=0)
    Estado: str = Field(default="activo", max_length=20)
    Foto: Optional[str] = Field(None, max_length=500)
    
    @validator('Nombre', 'Apellido', 'Cargo', 'Departamento', 'Genero')
    def sanitize_text(cls, v):
        if v is None:
            return None
        return sanitize_string(v, max_length=100)
    
    @validator('Telefono')
    def validate_phone(cls, v):
        v = sanitize_string(v, max_length=20)
        if not validate_phone(v):
            raise ValueError('Formato de teléfono inválido')
        return v
    
    @validator('FechaContratacion', 'FechaNacimiento')
    def validate_date(cls, v):
        if v is None:
            return None
        if len(v) != 10 or v[4] != '-' or v[7] != '-':
            raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD')
        return v
    
    @validator('Estado')
    def validate_estado(cls, v):
        estados_validos = ['activo', 'suspendido', 'retirado']
        if v not in estados_validos:
            raise ValueError(f'Estado debe ser uno de: {", ".join(estados_validos)}')
        return v


class EmpleadoResponse(BaseModel):
    IdEmpleado: Optional[int]
    Nombre: str
    Apellido: str
    FechaNacimiento: Optional[str]
    Genero: Optional[str]
    Telefono: str
    Email: str
    Direccion: Optional[str]
    Cedula: Optional[str]
    Cargo: str
    Departamento: str
    FechaContratacion: str
    Salario: Optional[float]
    Estado: str
    Foto: Optional[str]


@router.post("/", response_model=dict)
def crear_empleado(empleado: Empleado, current_user: dict = Depends(get_current_active_user)):
    """Crear un nuevo empleado"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Empleados (
                Nombre, Apellido, FechaNacimiento, Genero, Telefono, Email,
                Direccion, Cedula, Cargo, Departamento, FechaContratacion,
                Salario, Estado, Foto
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            empleado.Nombre, empleado.Apellido, empleado.FechaNacimiento,
            empleado.Genero, empleado.Telefono, empleado.Email,
            empleado.Direccion, empleado.Cedula, empleado.Cargo,
            empleado.Departamento, empleado.FechaContratacion,
            empleado.Salario, empleado.Estado, empleado.Foto
        ))
        conn.commit()
        empleado_id = cursor.lastrowid
        logger.info(f"Empleado creado: ID {empleado_id}")
        return {"mensaje": "Empleado creado exitosamente", "IdEmpleado": empleado_id}
    except Exception as e:
        logger.error(f"Error al crear empleado: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/", response_model=List[EmpleadoResponse])
def obtener_empleados(current_user: dict = Depends(get_current_active_user)):
    """Obtener todos los empleados"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Empleados ORDER BY Nombre, Apellido")
        rows = cursor.fetchall()
        return [
            {
                "IdEmpleado": row["IdEmpleado"],
                "Nombre": row["Nombre"],
                "Apellido": row["Apellido"],
                "FechaNacimiento": row["FechaNacimiento"],
                "Genero": row["Genero"],
                "Telefono": row["Telefono"],
                "Email": row["Email"],
                "Direccion": row["Direccion"],
                "Cedula": row["Cedula"],
                "Cargo": row["Cargo"],
                "Departamento": row["Departamento"],
                "FechaContratacion": row["FechaContratacion"],
                "Salario": row["Salario"],
                "Estado": row["Estado"],
                "Foto": row["Foto"]
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error al obtener empleados: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=EmpleadoResponse)
def obtener_empleado(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener un empleado por ID"""
    if id <= 0:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Empleados WHERE IdEmpleado = ?", (id,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        return {
            "IdEmpleado": row["IdEmpleado"],
            "Nombre": row["Nombre"],
            "Apellido": row["Apellido"],
            "FechaNacimiento": row["FechaNacimiento"],
            "Genero": row["Genero"],
            "Telefono": row["Telefono"],
            "Email": row["Email"],
            "Direccion": row["Direccion"],
            "Cedula": row["Cedula"],
            "Cargo": row["Cargo"],
            "Departamento": row["Departamento"],
            "FechaContratacion": row["FechaContratacion"],
            "Salario": row["Salario"],
            "Estado": row["Estado"],
            "Foto": row["Foto"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener empleado {id}: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_empleado(id: int, empleado: Empleado, current_user: dict = Depends(get_current_active_user)):
    """Actualizar un empleado existente"""
    if id <= 0:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Empleados
            SET Nombre = ?, Apellido = ?, FechaNacimiento = ?, Genero = ?,
                Telefono = ?, Email = ?, Direccion = ?, Cedula = ?,
                Cargo = ?, Departamento = ?, FechaContratacion = ?,
                Salario = ?, Estado = ?, Foto = ?
            WHERE IdEmpleado = ?
        """, (
            empleado.Nombre, empleado.Apellido, empleado.FechaNacimiento,
            empleado.Genero, empleado.Telefono, empleado.Email,
            empleado.Direccion, empleado.Cedula, empleado.Cargo,
            empleado.Departamento, empleado.FechaContratacion,
            empleado.Salario, empleado.Estado, empleado.Foto, id
        ))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        conn.commit()
        logger.info(f"Empleado actualizado: ID {id}")
        return {"mensaje": "Empleado actualizado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar empleado {id}: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_empleado(id: int, current_user: dict = Depends(get_current_active_user)):
    """Eliminar un empleado"""
    if id <= 0:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Verificar si hay registros de asistencia asociados
        cursor.execute("SELECT COUNT(*) FROM Asistencia WHERE IdEmpleado = ?", (id,))
        asistencia_count = cursor.fetchone()[0]
        if asistencia_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede eliminar el empleado porque tiene {asistencia_count} registro(s) de asistencia asociado(s)"
            )
        
        cursor.execute("DELETE FROM Empleados WHERE IdEmpleado = ?", (id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        conn.commit()
        logger.info(f"Empleado eliminado: ID {id}")
        return {"mensaje": "Empleado eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar empleado {id}: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

