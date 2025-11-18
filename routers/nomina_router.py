"""
Router para gestión de Nómina
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models.nomina import Nomina, NominaResponse, DetalleNomina, DetalleNominaResponse
from database import get_db_connection
from auth import get_current_active_user
from security import safe_error_message
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/nomina", tags=["nomina"])


@router.get("/", response_model=List[NominaResponse])
def obtener_nominas(current_user: dict = Depends(get_current_active_user)):
    """Obtener todas las nóminas"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Nominas ORDER BY Periodo DESC, FechaPago DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener nóminas: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=NominaResponse)
def obtener_nomina(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener una nómina por ID"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Nominas WHERE IdNomina = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Nómina no encontrada")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener nómina: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/periodo/{periodo}", response_model=List[NominaResponse])
def obtener_nominas_por_periodo(periodo: str, current_user: dict = Depends(get_current_active_user)):
    """Obtener nóminas por período"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Nominas WHERE Periodo = ? ORDER BY FechaPago DESC", (periodo,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener nóminas por período: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/estado/{estado}", response_model=List[NominaResponse])
def obtener_nominas_por_estado(estado: str, current_user: dict = Depends(get_current_active_user)):
    """Obtener nóminas por estado"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Nominas WHERE Estado = ? ORDER BY Periodo DESC", (estado,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener nóminas por estado: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/empleado/{id_empleado}", response_model=List[NominaResponse])
def obtener_nominas_por_empleado(id_empleado: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener nóminas por empleado"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT n.* FROM Nominas n
            INNER JOIN DetallesNomina d ON n.IdNomina = d.IdNomina
            WHERE d.IdEmpleado = ?
            ORDER BY n.Periodo DESC
        """, (id_empleado,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener nóminas por empleado: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}/detalles", response_model=List[DetalleNominaResponse])
def obtener_detalles_nomina(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener detalles de una nómina"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DetallesNomina WHERE IdNomina = ? ORDER BY IdEmpleado", (id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener detalles de nómina: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_nomina(nomina: Nomina, current_user: dict = Depends(get_current_active_user)):
    """Crear una nueva nómina"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Nominas (Periodo, FechaInicio, FechaFin, FechaPago, TipoNomina, Estado,
                               TotalEmpleados, TotalDevengado, TotalDeducido, TotalNeto, Observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            nomina.Periodo,
            nomina.FechaInicio,
            nomina.FechaFin,
            nomina.FechaPago,
            nomina.TipoNomina,
            nomina.Estado,
            nomina.TotalEmpleados,
            nomina.TotalDevengado,
            nomina.TotalDeducido,
            nomina.TotalNeto,
            nomina.Observaciones
        ))
        nomina_id = cursor.lastrowid
        conn.commit()
        return {"mensaje": "Nómina creada exitosamente", "IdNomina": nomina_id}
    except Exception as e:
        logger.error(f"Error al crear nómina: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_nomina(id: int, nomina: Nomina, current_user: dict = Depends(get_current_active_user)):
    """Actualizar una nómina"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdNomina FROM Nominas WHERE IdNomina = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Nómina no encontrada")
        
        cursor.execute("""
            UPDATE Nominas 
            SET Periodo = ?, FechaInicio = ?, FechaFin = ?, FechaPago = ?, TipoNomina = ?, Estado = ?,
                TotalEmpleados = ?, TotalDevengado = ?, TotalDeducido = ?, TotalNeto = ?, Observaciones = ?,
                FechaActualizacion = ?
            WHERE IdNomina = ?
        """, (
            nomina.Periodo,
            nomina.FechaInicio,
            nomina.FechaFin,
            nomina.FechaPago,
            nomina.TipoNomina,
            nomina.Estado,
            nomina.TotalEmpleados,
            nomina.TotalDevengado,
            nomina.TotalDeducido,
            nomina.TotalNeto,
            nomina.Observaciones,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            id
        ))
        conn.commit()
        return {"mensaje": "Nómina actualizada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar nómina: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/{id}/calcular", response_model=dict)
def calcular_nomina(id: int, current_user: dict = Depends(get_current_active_user)):
    """Calcular una nómina (simplificado - en producción debería calcular todos los detalles)"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdNomina FROM Nominas WHERE IdNomina = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Nómina no encontrada")
        
        # Calcular totales desde detalles
        cursor.execute("""
            SELECT 
                COUNT(*) as TotalEmpleados,
                SUM(TotalDevengado) as TotalDevengado,
                SUM(TotalDeducido) as TotalDeducido,
                SUM(NetoAPagar) as TotalNeto
            FROM DetallesNomina
            WHERE IdNomina = ?
        """, (id,))
        resultado = cursor.fetchone()
        
        total_empleados = resultado[0] or 0
        total_devengado = resultado[1] or 0.0
        total_deducido = resultado[2] or 0.0
        total_neto = resultado[3] or 0.0
        
        cursor.execute("""
            UPDATE Nominas 
            SET Estado = 'calculada', TotalEmpleados = ?, TotalDevengado = ?, TotalDeducido = ?, TotalNeto = ?,
                FechaActualizacion = ?
            WHERE IdNomina = ?
        """, (
            total_empleados,
            total_devengado,
            total_deducido,
            total_neto,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            id
        ))
        conn.commit()
        return {"mensaje": "Nómina calculada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al calcular nómina: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/{id}/pagar", response_model=dict)
def pagar_nomina(id: int, current_user: dict = Depends(get_current_active_user)):
    """Marcar una nómina como pagada"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdNomina FROM Nominas WHERE IdNomina = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Nómina no encontrada")
        
        cursor.execute("""
            UPDATE Nominas 
            SET Estado = 'pagada', FechaActualizacion = ?
            WHERE IdNomina = ?
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id))
        conn.commit()
        return {"mensaje": "Nómina marcada como pagada"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al pagar nómina: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}/recibo/{id_empleado}", response_model=DetalleNominaResponse)
def obtener_recibo(id: int, id_empleado: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener recibo de pago de un empleado"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM DetallesNomina 
            WHERE IdNomina = ? AND IdEmpleado = ?
        """, (id, id_empleado))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Recibo no encontrado")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener recibo: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_nomina(id: int, current_user: dict = Depends(get_current_active_user)):
    """Eliminar una nómina"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdNomina FROM Nominas WHERE IdNomina = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Nómina no encontrada")
        
        # Eliminar detalles asociados
        cursor.execute("DELETE FROM DetallesNomina WHERE IdNomina = ?", (id,))
        
        cursor.execute("DELETE FROM Nominas WHERE IdNomina = ?", (id,))
        conn.commit()
        return {"mensaje": "Nómina eliminada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar nómina: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

