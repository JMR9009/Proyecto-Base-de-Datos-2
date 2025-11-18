"""
Router para gestión de Contratos
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models.contrato import Contrato, ContratoResponse
from database import get_db_connection
from auth import get_current_active_user
from security import safe_error_message
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/contratos", tags=["contratos"])


def validate_empleado_exists(cursor, id_empleado: int):
    """Validar que el empleado existe"""
    cursor.execute("SELECT IdEmpleado FROM Empleados WHERE IdEmpleado = ?", (id_empleado,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Empleado no encontrado")


@router.get("/", response_model=List[ContratoResponse])
def obtener_contratos(current_user: dict = Depends(get_current_active_user)):
    """Obtener todos los contratos"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Contratos ORDER BY FechaInicio DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener contratos: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=ContratoResponse)
def obtener_contrato(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener un contrato por ID"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Contratos WHERE IdContrato = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Contrato no encontrado")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener contrato: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/empleado/{id_empleado}", response_model=List[ContratoResponse])
def obtener_contratos_por_empleado(id_empleado: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener contratos por empleado"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        validate_empleado_exists(cursor, id_empleado)
        cursor.execute("SELECT * FROM Contratos WHERE IdEmpleado = ? ORDER BY FechaInicio DESC", (id_empleado,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener contratos por empleado: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/vigentes", response_model=List[ContratoResponse])
def obtener_contratos_vigentes(current_user: dict = Depends(get_current_active_user)):
    """Obtener contratos vigentes"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        hoy = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT * FROM Contratos 
            WHERE Estado = 'vigente' 
            AND (FechaFin IS NULL OR FechaFin >= ?)
            ORDER BY FechaFin ASC
        """, (hoy,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener contratos vigentes: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/por-vencer", response_model=List[ContratoResponse])
def obtener_contratos_por_vencer(current_user: dict = Depends(get_current_active_user)):
    """Obtener contratos por vencer (próximos 30 días)"""
    conn = None
    try:
        from datetime import timedelta
        conn = get_db_connection()
        cursor = conn.cursor()
        hoy = datetime.now().strftime("%Y-%m-%d")
        fecha_limite = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT * FROM Contratos 
            WHERE Estado = 'vigente' 
            AND FechaFin IS NOT NULL
            AND FechaFin >= ? AND FechaFin <= ?
            ORDER BY FechaFin ASC
        """, (hoy, fecha_limite))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener contratos por vencer: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_contrato(contrato: Contrato, current_user: dict = Depends(get_current_active_user)):
    """Crear un nuevo contrato"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        validate_empleado_exists(cursor, contrato.IdEmpleado)
        
        cursor.execute("""
            INSERT INTO Contratos (IdEmpleado, TipoContrato, NumeroContrato, FechaInicio, FechaFin, 
                                  Salario, Moneda, HorasSemana, Descripcion, Condiciones, Estado, 
                                  FechaFirma, DocumentoUrl, Observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contrato.IdEmpleado,
            contrato.TipoContrato,
            contrato.NumeroContrato,
            contrato.FechaInicio,
            contrato.FechaFin,
            contrato.Salario,
            contrato.Moneda,
            contrato.HorasSemana,
            contrato.Descripcion,
            contrato.Condiciones,
            contrato.Estado,
            contrato.FechaFirma,
            contrato.DocumentoUrl,
            contrato.Observaciones
        ))
        contrato_id = cursor.lastrowid
        conn.commit()
        return {"mensaje": "Contrato creado exitosamente", "IdContrato": contrato_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear contrato: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_contrato(id: int, contrato: Contrato, current_user: dict = Depends(get_current_active_user)):
    """Actualizar un contrato"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdContrato FROM Contratos WHERE IdContrato = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Contrato no encontrado")
        
        validate_empleado_exists(cursor, contrato.IdEmpleado)
        
        cursor.execute("""
            UPDATE Contratos 
            SET IdEmpleado = ?, TipoContrato = ?, NumeroContrato = ?, FechaInicio = ?, FechaFin = ?,
                Salario = ?, Moneda = ?, HorasSemana = ?, Descripcion = ?, Condiciones = ?, Estado = ?,
                FechaFirma = ?, DocumentoUrl = ?, Observaciones = ?
            WHERE IdContrato = ?
        """, (
            contrato.IdEmpleado,
            contrato.TipoContrato,
            contrato.NumeroContrato,
            contrato.FechaInicio,
            contrato.FechaFin,
            contrato.Salario,
            contrato.Moneda,
            contrato.HorasSemana,
            contrato.Descripcion,
            contrato.Condiciones,
            contrato.Estado,
            contrato.FechaFirma,
            contrato.DocumentoUrl,
            contrato.Observaciones,
            id
        ))
        conn.commit()
        return {"mensaje": "Contrato actualizado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar contrato: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_contrato(id: int, current_user: dict = Depends(get_current_active_user)):
    """Eliminar un contrato"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdContrato FROM Contratos WHERE IdContrato = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Contrato no encontrado")
        
        cursor.execute("DELETE FROM Contratos WHERE IdContrato = ?", (id,))
        conn.commit()
        return {"mensaje": "Contrato eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar contrato: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/{id}/renovar", response_model=dict)
def renovar_contrato(id: int, nuevo_contrato: Contrato, current_user: dict = Depends(get_current_active_user)):
    """Renovar un contrato (marcar el anterior como renovado y crear uno nuevo)"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que el contrato existe
        cursor.execute("SELECT IdContrato FROM Contratos WHERE IdContrato = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Contrato no encontrado")
        
        # Marcar el contrato anterior como renovado
        cursor.execute("UPDATE Contratos SET Estado = 'renovado' WHERE IdContrato = ?", (id,))
        
        # Crear el nuevo contrato
        validate_empleado_exists(cursor, nuevo_contrato.IdEmpleado)
        cursor.execute("""
            INSERT INTO Contratos (IdEmpleado, TipoContrato, NumeroContrato, FechaInicio, FechaFin, 
                                  Salario, Moneda, HorasSemana, Descripcion, Condiciones, Estado, 
                                  FechaFirma, DocumentoUrl, Observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            nuevo_contrato.IdEmpleado,
            nuevo_contrato.TipoContrato,
            nuevo_contrato.NumeroContrato,
            nuevo_contrato.FechaInicio,
            nuevo_contrato.FechaFin,
            nuevo_contrato.Salario,
            nuevo_contrato.Moneda,
            nuevo_contrato.HorasSemana,
            nuevo_contrato.Descripcion,
            nuevo_contrato.Condiciones,
            nuevo_contrato.Estado,
            nuevo_contrato.FechaFirma,
            nuevo_contrato.DocumentoUrl,
            nuevo_contrato.Observaciones
        ))
        nuevo_contrato_id = cursor.lastrowid
        conn.commit()
        return {"mensaje": "Contrato renovado exitosamente", "IdContratoAnterior": id, "IdContratoNuevo": nuevo_contrato_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al renovar contrato: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

