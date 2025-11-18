"""
Router para gestión de Capacitaciones
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models.capacitacion import Capacitacion, CapacitacionResponse
from database import get_db_connection
from auth import get_current_active_user
from security import safe_error_message
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/capacitaciones", tags=["capacitaciones"])


@router.get("/", response_model=List[CapacitacionResponse])
def obtener_capacitaciones(current_user: dict = Depends(get_current_active_user)):
    """Obtener todas las capacitaciones"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Capacitaciones ORDER BY FechaInicio DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener capacitaciones: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=CapacitacionResponse)
def obtener_capacitacion(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener una capacitación por ID"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Capacitaciones WHERE IdCapacitacion = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Capacitación no encontrada")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener capacitación: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/estado/{estado}", response_model=List[CapacitacionResponse])
def obtener_capacitaciones_por_estado(estado: str, current_user: dict = Depends(get_current_active_user)):
    """Obtener capacitaciones por estado"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Capacitaciones WHERE Estado = ? ORDER BY FechaInicio DESC", (estado,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener capacitaciones por estado: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/proximas", response_model=List[CapacitacionResponse])
def obtener_capacitaciones_proximas(current_user: dict = Depends(get_current_active_user)):
    """Obtener capacitaciones próximas"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        hoy = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT * FROM Capacitaciones 
            WHERE Estado = 'programada' AND FechaInicio >= ?
            ORDER BY FechaInicio ASC
        """, (hoy,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener capacitaciones próximas: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/en-curso", response_model=List[CapacitacionResponse])
def obtener_capacitaciones_en_curso(current_user: dict = Depends(get_current_active_user)):
    """Obtener capacitaciones en curso"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Capacitaciones WHERE Estado = 'en_curso' ORDER BY FechaInicio DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener capacitaciones en curso: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_capacitacion(capacitacion: Capacitacion, current_user: dict = Depends(get_current_active_user)):
    """Crear una nueva capacitación"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Capacitaciones (Nombre, Descripcion, Tipo, Modalidad, DuracionHoras, FechaInicio, FechaFin,
                                       Instructor, Lugar, Costo, Estado, CapacidadMaxima, Requisitos, Objetivos, Certificado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            capacitacion.Nombre,
            capacitacion.Descripcion,
            capacitacion.Tipo,
            capacitacion.Modalidad,
            capacitacion.DuracionHoras,
            capacitacion.FechaInicio,
            capacitacion.FechaFin,
            capacitacion.Instructor,
            capacitacion.Lugar,
            capacitacion.Costo,
            capacitacion.Estado,
            capacitacion.CapacidadMaxima,
            capacitacion.Requisitos,
            capacitacion.Objetivos,
            1 if capacitacion.Certificado else 0
        ))
        capacitacion_id = cursor.lastrowid
        conn.commit()
        return {"mensaje": "Capacitación creada exitosamente", "IdCapacitacion": capacitacion_id}
    except Exception as e:
        logger.error(f"Error al crear capacitación: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_capacitacion(id: int, capacitacion: Capacitacion, current_user: dict = Depends(get_current_active_user)):
    """Actualizar una capacitación"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdCapacitacion FROM Capacitaciones WHERE IdCapacitacion = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Capacitación no encontrada")
        
        cursor.execute("""
            UPDATE Capacitaciones 
            SET Nombre = ?, Descripcion = ?, Tipo = ?, Modalidad = ?, DuracionHoras = ?, FechaInicio = ?, FechaFin = ?,
                Instructor = ?, Lugar = ?, Costo = ?, Estado = ?, CapacidadMaxima = ?, Requisitos = ?, Objetivos = ?, Certificado = ?
            WHERE IdCapacitacion = ?
        """, (
            capacitacion.Nombre,
            capacitacion.Descripcion,
            capacitacion.Tipo,
            capacitacion.Modalidad,
            capacitacion.DuracionHoras,
            capacitacion.FechaInicio,
            capacitacion.FechaFin,
            capacitacion.Instructor,
            capacitacion.Lugar,
            capacitacion.Costo,
            capacitacion.Estado,
            capacitacion.CapacidadMaxima,
            capacitacion.Requisitos,
            capacitacion.Objetivos,
            1 if capacitacion.Certificado else 0,
            id
        ))
        conn.commit()
        return {"mensaje": "Capacitación actualizada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar capacitación: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_capacitacion(id: int, current_user: dict = Depends(get_current_active_user)):
    """Eliminar una capacitación"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdCapacitacion FROM Capacitaciones WHERE IdCapacitacion = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Capacitación no encontrada")
        
        # Verificar si tiene asignaciones asociadas
        cursor.execute("SELECT COUNT(*) FROM AsignacionesCapacitacion WHERE IdCapacitacion = ?", (id,))
        if cursor.fetchone()[0] > 0:
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar la capacitación porque tiene asignaciones asociadas"
            )
        
        cursor.execute("DELETE FROM Capacitaciones WHERE IdCapacitacion = ?", (id,))
        conn.commit()
        return {"mensaje": "Capacitación eliminada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar capacitación: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

