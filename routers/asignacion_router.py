"""
Router para gestión de Asignaciones de Empleados
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models.asignacion_empleado import AsignacionEmpleado, AsignacionEmpleadoResponse
from database import get_db_connection
from auth import get_current_active_user
from security import safe_error_message
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/asignaciones", tags=["asignaciones"])


def validate_references(cursor, id_empleado: int, id_departamento: int, id_puesto: int):
    """Validar que las referencias existen"""
    cursor.execute("SELECT IdEmpleado FROM Empleados WHERE IdEmpleado = ?", (id_empleado,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    
    cursor.execute("SELECT IdDepartamento FROM Departamentos WHERE IdDepartamento = ?", (id_departamento,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    
    cursor.execute("SELECT IdPuesto FROM Puestos WHERE IdPuesto = ?", (id_puesto,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Puesto no encontrado")


@router.get("/", response_model=List[AsignacionEmpleadoResponse])
def obtener_asignaciones(current_user: dict = Depends(get_current_active_user)):
    """Obtener todas las asignaciones"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM AsignacionesEmpleados ORDER BY FechaAsignacion DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener asignaciones: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=AsignacionEmpleadoResponse)
def obtener_asignacion(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener una asignación por ID"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM AsignacionesEmpleados WHERE IdAsignacion = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Asignación no encontrada")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener asignación: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/departamento/{id_departamento}", response_model=List[AsignacionEmpleadoResponse])
def obtener_asignaciones_por_departamento(id_departamento: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener asignaciones por departamento"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM AsignacionesEmpleados WHERE IdDepartamento = ? ORDER BY FechaAsignacion DESC", (id_departamento,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener asignaciones por departamento: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/empleado/{id_empleado}", response_model=List[AsignacionEmpleadoResponse])
def obtener_asignaciones_por_empleado(id_empleado: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener asignaciones por empleado"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM AsignacionesEmpleados WHERE IdEmpleado = ? ORDER BY FechaAsignacion DESC", (id_empleado,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener asignaciones por empleado: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_asignacion(asignacion: AsignacionEmpleado, current_user: dict = Depends(get_current_active_user)):
    """Crear una nueva asignación"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        validate_references(cursor, asignacion.IdEmpleado, asignacion.IdDepartamento, asignacion.IdPuesto)
        
        fecha_asignacion = asignacion.FechaAsignacion or datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute("""
            INSERT INTO AsignacionesEmpleados (IdEmpleado, IdDepartamento, IdPuesto, FechaAsignacion, Estado)
            VALUES (?, ?, ?, ?, ?)
        """, (
            asignacion.IdEmpleado,
            asignacion.IdDepartamento,
            asignacion.IdPuesto,
            fecha_asignacion,
            asignacion.Estado
        ))
        asignacion_id = cursor.lastrowid
        conn.commit()
        return {"mensaje": "Asignación creada exitosamente", "IdAsignacion": asignacion_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear asignación: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_asignacion(id: int, asignacion: AsignacionEmpleado, current_user: dict = Depends(get_current_active_user)):
    """Actualizar una asignación"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdAsignacion FROM AsignacionesEmpleados WHERE IdAsignacion = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Asignación no encontrada")
        
        validate_references(cursor, asignacion.IdEmpleado, asignacion.IdDepartamento, asignacion.IdPuesto)
        
        cursor.execute("""
            UPDATE AsignacionesEmpleados 
            SET IdEmpleado = ?, IdDepartamento = ?, IdPuesto = ?, FechaAsignacion = ?, Estado = ?
            WHERE IdAsignacion = ?
        """, (
            asignacion.IdEmpleado,
            asignacion.IdDepartamento,
            asignacion.IdPuesto,
            asignacion.FechaAsignacion,
            asignacion.Estado,
            id
        ))
        conn.commit()
        return {"mensaje": "Asignación actualizada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar asignación: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_asignacion(id: int, current_user: dict = Depends(get_current_active_user)):
    """Eliminar una asignación"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdAsignacion FROM AsignacionesEmpleados WHERE IdAsignacion = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Asignación no encontrada")
        
        cursor.execute("DELETE FROM AsignacionesEmpleados WHERE IdAsignacion = ?", (id,))
        conn.commit()
        return {"mensaje": "Asignación eliminada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar asignación: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

