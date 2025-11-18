"""
Router para gestión de Asignaciones de Capacitación
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models.asignacion_capacitacion import AsignacionCapacitacion, AsignacionCapacitacionResponse
from database import get_db_connection
from auth import get_current_active_user
from security import safe_error_message
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/asignaciones-capacitacion", tags=["asignaciones-capacitacion"])


def validate_references(cursor, id_capacitacion: int, id_empleado: int):
    """Validar que las referencias existen"""
    cursor.execute("SELECT IdCapacitacion FROM Capacitaciones WHERE IdCapacitacion = ?", (id_capacitacion,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Capacitación no encontrada")
    
    cursor.execute("SELECT IdEmpleado FROM Empleados WHERE IdEmpleado = ?", (id_empleado,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Empleado no encontrado")


@router.get("/", response_model=List[AsignacionCapacitacionResponse])
def obtener_asignaciones(current_user: dict = Depends(get_current_active_user)):
    """Obtener todas las asignaciones de capacitación"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM AsignacionesCapacitacion ORDER BY FechaAsignacion DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener asignaciones: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=AsignacionCapacitacionResponse)
def obtener_asignacion(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener una asignación por ID"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM AsignacionesCapacitacion WHERE IdAsignacion = ?", (id,))
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


@router.get("/capacitacion/{id_capacitacion}", response_model=List[AsignacionCapacitacionResponse])
def obtener_asignaciones_por_capacitacion(id_capacitacion: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener asignaciones por capacitación"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM AsignacionesCapacitacion WHERE IdCapacitacion = ? ORDER BY FechaAsignacion DESC", (id_capacitacion,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener asignaciones por capacitación: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/empleado/{id_empleado}", response_model=List[AsignacionCapacitacionResponse])
def obtener_asignaciones_por_empleado(id_empleado: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener asignaciones por empleado"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM AsignacionesCapacitacion WHERE IdEmpleado = ? ORDER BY FechaAsignacion DESC", (id_empleado,))
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
def asignar_capacitacion(asignacion: AsignacionCapacitacion, current_user: dict = Depends(get_current_active_user)):
    """Asignar una capacitación a un empleado"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        validate_references(cursor, asignacion.IdCapacitacion, asignacion.IdEmpleado)
        
        cursor.execute("""
            INSERT INTO AsignacionesCapacitacion (IdCapacitacion, IdEmpleado, FechaAsignacion, Estado, Calificacion, 
                                                  Asistencia, Observaciones, CertificadoUrl, FechaCompletacion, 
                                                  FechaEmisionCertificado, NumeroCertificado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            asignacion.IdCapacitacion,
            asignacion.IdEmpleado,
            asignacion.FechaAsignacion,
            asignacion.Estado,
            asignacion.Calificacion,
            asignacion.Asistencia,
            asignacion.Observaciones,
            asignacion.CertificadoUrl,
            asignacion.FechaCompletacion,
            asignacion.FechaEmisionCertificado,
            asignacion.NumeroCertificado
        ))
        asignacion_id = cursor.lastrowid
        conn.commit()
        return {"mensaje": "Capacitación asignada exitosamente", "IdAsignacion": asignacion_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al asignar capacitación: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_asignacion(id: int, asignacion: AsignacionCapacitacion, current_user: dict = Depends(get_current_active_user)):
    """Actualizar una asignación"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdAsignacion FROM AsignacionesCapacitacion WHERE IdAsignacion = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Asignación no encontrada")
        
        validate_references(cursor, asignacion.IdCapacitacion, asignacion.IdEmpleado)
        
        cursor.execute("""
            UPDATE AsignacionesCapacitacion 
            SET IdCapacitacion = ?, IdEmpleado = ?, FechaAsignacion = ?, Estado = ?, Calificacion = ?,
                Asistencia = ?, Observaciones = ?, CertificadoUrl = ?, FechaCompletacion = ?,
                FechaEmisionCertificado = ?, NumeroCertificado = ?
            WHERE IdAsignacion = ?
        """, (
            asignacion.IdCapacitacion,
            asignacion.IdEmpleado,
            asignacion.FechaAsignacion,
            asignacion.Estado,
            asignacion.Calificacion,
            asignacion.Asistencia,
            asignacion.Observaciones,
            asignacion.CertificadoUrl,
            asignacion.FechaCompletacion,
            asignacion.FechaEmisionCertificado,
            asignacion.NumeroCertificado,
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


@router.put("/{id}/asistencia", response_model=dict)
def registrar_asistencia(id: int, data: dict, current_user: dict = Depends(get_current_active_user)):
    """Registrar asistencia de una asignación"""
    conn = None
    try:
        from pydantic import BaseModel
        asistencia = data.get("Asistencia")
        if asistencia is None:
            raise HTTPException(status_code=400, detail="El campo Asistencia es requerido")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdAsignacion FROM AsignacionesCapacitacion WHERE IdAsignacion = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Asignación no encontrada")
        
        if asistencia < 0 or asistencia > 100:
            raise HTTPException(status_code=400, detail="La asistencia debe estar entre 0 y 100")
        
        cursor.execute("UPDATE AsignacionesCapacitacion SET Asistencia = ? WHERE IdAsignacion = ?", (asistencia, id))
        conn.commit()
        return {"mensaje": "Asistencia registrada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al registrar asistencia: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}/completar", response_model=dict)
def completar_asignacion(id: int, asignacion: AsignacionCapacitacion, current_user: dict = Depends(get_current_active_user)):
    """Completar una asignación de capacitación"""
    conn = None
    try:
        from datetime import datetime
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdAsignacion FROM AsignacionesCapacitacion WHERE IdAsignacion = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Asignación no encontrada")
        
        fecha_completacion = asignacion.FechaCompletacion or datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute("""
            UPDATE AsignacionesCapacitacion 
            SET Estado = 'completada', Calificacion = ?, Asistencia = ?, Observaciones = ?,
                CertificadoUrl = ?, FechaCompletacion = ?, FechaEmisionCertificado = ?, NumeroCertificado = ?
            WHERE IdAsignacion = ?
        """, (
            asignacion.Calificacion,
            asignacion.Asistencia,
            asignacion.Observaciones,
            asignacion.CertificadoUrl,
            fecha_completacion,
            asignacion.FechaEmisionCertificado,
            asignacion.NumeroCertificado,
            id
        ))
        conn.commit()
        return {"mensaje": "Asignación completada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al completar asignación: {str(e)}", exc_info=True)
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
        
        cursor.execute("SELECT IdAsignacion FROM AsignacionesCapacitacion WHERE IdAsignacion = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Asignación no encontrada")
        
        cursor.execute("DELETE FROM AsignacionesCapacitacion WHERE IdAsignacion = ?", (id,))
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

