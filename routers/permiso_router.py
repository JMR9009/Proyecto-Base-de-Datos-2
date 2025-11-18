"""
Router para gestión de Permisos
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from models.vacacion_permiso import SolicitudPermiso, SolicitudPermisoResponse
from database import get_db_connection
from auth import get_current_active_user
from security import safe_error_message
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/permisos", tags=["permisos"])


def validate_empleado_exists(cursor, id_empleado: int):
    """Validar que el empleado existe"""
    cursor.execute("SELECT IdEmpleado FROM Empleados WHERE IdEmpleado = ?", (id_empleado,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Empleado no encontrado")


@router.get("/", response_model=List[SolicitudPermisoResponse])
def obtener_solicitudes_permisos(current_user: dict = Depends(get_current_active_user)):
    """Obtener todas las solicitudes de permisos"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SolicitudesPermiso ORDER BY FechaCreacion DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener solicitudes de permisos: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=SolicitudPermisoResponse)
def obtener_solicitud_permiso(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener una solicitud de permiso por ID"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SolicitudesPermiso WHERE IdSolicitudPermiso = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Solicitud de permiso no encontrada")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener solicitud de permiso: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/empleado/{id_empleado}", response_model=List[SolicitudPermisoResponse])
def obtener_solicitudes_por_empleado(id_empleado: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener solicitudes de permisos por empleado"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        validate_empleado_exists(cursor, id_empleado)
        cursor.execute("SELECT * FROM SolicitudesPermiso WHERE IdEmpleado = ? ORDER BY FechaCreacion DESC", (id_empleado,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener solicitudes por empleado: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/estado/{estado}", response_model=List[SolicitudPermisoResponse])
def obtener_solicitudes_por_estado(estado: str, current_user: dict = Depends(get_current_active_user)):
    """Obtener solicitudes por estado"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SolicitudesPermiso WHERE Estado = ? ORDER BY FechaCreacion DESC", (estado,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener solicitudes por estado: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/tipo/{tipo}", response_model=List[SolicitudPermisoResponse])
def obtener_solicitudes_por_tipo(tipo: str, current_user: dict = Depends(get_current_active_user)):
    """Obtener solicitudes por tipo"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SolicitudesPermiso WHERE TipoPermiso = ? ORDER BY FechaCreacion DESC", (tipo,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener solicitudes por tipo: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/pendientes", response_model=List[SolicitudPermisoResponse])
def obtener_solicitudes_pendientes(current_user: dict = Depends(get_current_active_user)):
    """Obtener solicitudes pendientes"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SolicitudesPermiso WHERE Estado = 'pendiente' ORDER BY FechaCreacion ASC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener solicitudes pendientes: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_solicitud_permiso(solicitud: SolicitudPermiso, current_user: dict = Depends(get_current_active_user)):
    """Crear una nueva solicitud de permiso"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        validate_empleado_exists(cursor, solicitud.IdEmpleado)
        
        cursor.execute("""
            INSERT INTO SolicitudesPermiso (IdEmpleado, TipoPermiso, FechaInicio, FechaFin, HorasSolicitadas,
                                           DiasSolicitados, Motivo, Estado, IdAprobador, FechaAprobacion, ComentariosAprobador)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            solicitud.IdEmpleado,
            solicitud.TipoPermiso,
            solicitud.FechaInicio,
            solicitud.FechaFin,
            solicitud.HorasSolicitadas,
            solicitud.DiasSolicitados,
            solicitud.Motivo,
            solicitud.Estado,
            solicitud.IdAprobador,
            solicitud.FechaAprobacion,
            solicitud.ComentariosAprobador
        ))
        solicitud_id = cursor.lastrowid
        conn.commit()
        return {"mensaje": "Solicitud de permiso creada exitosamente", "IdSolicitudPermiso": solicitud_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear solicitud de permiso: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_solicitud_permiso(id: int, solicitud: SolicitudPermiso, current_user: dict = Depends(get_current_active_user)):
    """Actualizar una solicitud de permiso"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdSolicitudPermiso FROM SolicitudesPermiso WHERE IdSolicitudPermiso = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Solicitud de permiso no encontrada")
        
        validate_empleado_exists(cursor, solicitud.IdEmpleado)
        
        cursor.execute("""
            UPDATE SolicitudesPermiso 
            SET IdEmpleado = ?, TipoPermiso = ?, FechaInicio = ?, FechaFin = ?, HorasSolicitadas = ?,
                DiasSolicitados = ?, Motivo = ?, Estado = ?, IdAprobador = ?, FechaAprobacion = ?,
                ComentariosAprobador = ?, FechaActualizacion = ?
            WHERE IdSolicitudPermiso = ?
        """, (
            solicitud.IdEmpleado,
            solicitud.TipoPermiso,
            solicitud.FechaInicio,
            solicitud.FechaFin,
            solicitud.HorasSolicitadas,
            solicitud.DiasSolicitados,
            solicitud.Motivo,
            solicitud.Estado,
            solicitud.IdAprobador,
            solicitud.FechaAprobacion,
            solicitud.ComentariosAprobador,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            id
        ))
        conn.commit()
        return {"mensaje": "Solicitud de permiso actualizada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar solicitud de permiso: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/{id}/aprobar", response_model=dict)
def aprobar_solicitud_permiso(id: int, data: Optional[dict] = None, current_user: dict = Depends(get_current_active_user)):
    """Aprobar una solicitud de permiso"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdSolicitudPermiso FROM SolicitudesPermiso WHERE IdSolicitudPermiso = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Solicitud de permiso no encontrada")
        
        comentarios = data.get("comentarios") if data else None
        cursor.execute("""
            UPDATE SolicitudesPermiso 
            SET Estado = 'aprobada', IdAprobador = ?, FechaAprobacion = ?, ComentariosAprobador = ?, FechaActualizacion = ?
            WHERE IdSolicitudPermiso = ?
        """, (
            current_user.get("IdUsuario"),
            datetime.now().strftime("%Y-%m-%d"),
            comentarios,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            id
        ))
        conn.commit()
        return {"mensaje": "Solicitud de permiso aprobada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al aprobar solicitud de permiso: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/{id}/rechazar", response_model=dict)
def rechazar_solicitud_permiso(id: int, data: Optional[dict] = None, current_user: dict = Depends(get_current_active_user)):
    """Rechazar una solicitud de permiso"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdSolicitudPermiso FROM SolicitudesPermiso WHERE IdSolicitudPermiso = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Solicitud de permiso no encontrada")
        
        comentarios = data.get("comentarios") if data else None
        cursor.execute("""
            UPDATE SolicitudesPermiso 
            SET Estado = 'rechazada', IdAprobador = ?, FechaAprobacion = ?, ComentariosAprobador = ?, FechaActualizacion = ?
            WHERE IdSolicitudPermiso = ?
        """, (
            current_user.get("IdUsuario"),
            datetime.now().strftime("%Y-%m-%d"),
            comentarios,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            id
        ))
        conn.commit()
        return {"mensaje": "Solicitud de permiso rechazada"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al rechazar solicitud de permiso: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/{id}/cancelar", response_model=dict)
def cancelar_solicitud_permiso(id: int, current_user: dict = Depends(get_current_active_user)):
    """Cancelar una solicitud de permiso"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdSolicitudPermiso FROM SolicitudesPermiso WHERE IdSolicitudPermiso = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Solicitud de permiso no encontrada")
        
        cursor.execute("""
            UPDATE SolicitudesPermiso 
            SET Estado = 'cancelada', FechaActualizacion = ?
            WHERE IdSolicitudPermiso = ?
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id))
        conn.commit()
        return {"mensaje": "Solicitud de permiso cancelada"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cancelar solicitud de permiso: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_solicitud_permiso(id: int, current_user: dict = Depends(get_current_active_user)):
    """Eliminar una solicitud de permiso"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdSolicitudPermiso FROM SolicitudesPermiso WHERE IdSolicitudPermiso = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Solicitud de permiso no encontrada")
        
        cursor.execute("DELETE FROM SolicitudesPermiso WHERE IdSolicitudPermiso = ?", (id,))
        conn.commit()
        return {"mensaje": "Solicitud de permiso eliminada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar solicitud de permiso: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

