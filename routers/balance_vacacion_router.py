"""
Router para gestión de Balance de Vacaciones
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models.vacacion_permiso import BalanceVacaciones, BalanceVacacionesResponse
from database import get_db_connection
from auth import get_current_active_user
from security import safe_error_message
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/balance-vacaciones", tags=["balance-vacaciones"])


def validate_empleado_exists(cursor, id_empleado: int):
    """Validar que el empleado existe"""
    cursor.execute("SELECT IdEmpleado FROM Empleados WHERE IdEmpleado = ?", (id_empleado,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Empleado no encontrado")


@router.get("/", response_model=List[BalanceVacacionesResponse])
def obtener_balances(current_user: dict = Depends(get_current_active_user)):
    """Obtener todos los balances de vacaciones"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM BalanceVacaciones ORDER BY Periodo DESC, IdEmpleado")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener balances: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/empleado/{id_empleado}", response_model=List[BalanceVacacionesResponse])
def obtener_balances_por_empleado(id_empleado: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener balances por empleado"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        validate_empleado_exists(cursor, id_empleado)
        cursor.execute("SELECT * FROM BalanceVacaciones WHERE IdEmpleado = ? ORDER BY Periodo DESC", (id_empleado,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener balances por empleado: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/periodo/{periodo}", response_model=List[BalanceVacacionesResponse])
def obtener_balances_por_periodo(periodo: str, current_user: dict = Depends(get_current_active_user)):
    """Obtener balances por período"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM BalanceVacaciones WHERE Periodo = ? ORDER BY IdEmpleado", (periodo,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener balances por período: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_balance(balance: BalanceVacaciones, current_user: dict = Depends(get_current_active_user)):
    """Crear un nuevo balance de vacaciones"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        validate_empleado_exists(cursor, balance.IdEmpleado)
        
        # Calcular días disponibles
        dias_disponibles = balance.DiasAsignados - balance.DiasTomados - balance.DiasPendientes
        
        cursor.execute("""
            INSERT INTO BalanceVacaciones (IdEmpleado, Periodo, DiasAsignados, DiasTomados, DiasPendientes,
                                          DiasDisponibles, DiasVencidos, FechaVencimiento)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            balance.IdEmpleado,
            balance.Periodo,
            balance.DiasAsignados,
            balance.DiasTomados,
            balance.DiasPendientes,
            dias_disponibles,
            balance.DiasVencidos,
            balance.FechaVencimiento
        ))
        balance_id = cursor.lastrowid
        conn.commit()
        return {"mensaje": "Balance creado exitosamente", "IdBalance": balance_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear balance: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_balance(id: int, balance: BalanceVacaciones, current_user: dict = Depends(get_current_active_user)):
    """Actualizar un balance"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdBalance FROM BalanceVacaciones WHERE IdBalance = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Balance no encontrado")
        
        validate_empleado_exists(cursor, balance.IdEmpleado)
        
        # Calcular días disponibles
        dias_disponibles = balance.DiasAsignados - balance.DiasTomados - balance.DiasPendientes
        
        cursor.execute("""
            UPDATE BalanceVacaciones 
            SET IdEmpleado = ?, Periodo = ?, DiasAsignados = ?, DiasTomados = ?, DiasPendientes = ?,
                DiasDisponibles = ?, DiasVencidos = ?, FechaVencimiento = ?
            WHERE IdBalance = ?
        """, (
            balance.IdEmpleado,
            balance.Periodo,
            balance.DiasAsignados,
            balance.DiasTomados,
            balance.DiasPendientes,
            dias_disponibles,
            balance.DiasVencidos,
            balance.FechaVencimiento,
            id
        ))
        conn.commit()
        return {"mensaje": "Balance actualizado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar balance: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/asignar", response_model=dict)
def asignar_dias_vacaciones(data: dict, current_user: dict = Depends(get_current_active_user)):
    """Asignar días de vacaciones a un empleado"""
    conn = None
    try:
        id_empleado = data.get("idEmpleado")
        periodo = data.get("periodo")
        dias = data.get("dias")
        
        if not id_empleado or not periodo or dias is None:
            raise HTTPException(status_code=400, detail="idEmpleado, periodo y dias son requeridos")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        validate_empleado_exists(cursor, id_empleado)
        
        # Verificar si ya existe un balance para este empleado y período
        cursor.execute("""
            SELECT IdBalance, DiasAsignados FROM BalanceVacaciones 
            WHERE IdEmpleado = ? AND Periodo = ?
        """, (id_empleado, periodo))
        row = cursor.fetchone()
        
        if row:
            # Actualizar balance existente
            balance_id = row[0]
            dias_actuales = row[1]
            nuevos_dias = dias_actuales + dias
            
            cursor.execute("""
                UPDATE BalanceVacaciones 
                SET DiasAsignados = ?, DiasDisponibles = DiasAsignados - DiasTomados - DiasPendientes
                WHERE IdBalance = ?
            """, (nuevos_dias, balance_id))
        else:
            # Crear nuevo balance
            cursor.execute("""
                INSERT INTO BalanceVacaciones (IdEmpleado, Periodo, DiasAsignados, DiasTomados, DiasPendientes, DiasDisponibles)
                VALUES (?, ?, ?, 0, 0, ?)
            """, (id_empleado, periodo, dias, dias))
        
        conn.commit()
        return {"mensaje": f"{dias} días de vacaciones asignados exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al asignar días de vacaciones: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_balance(id: int, current_user: dict = Depends(get_current_active_user)):
    """Eliminar un balance"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdBalance FROM BalanceVacaciones WHERE IdBalance = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Balance no encontrado")
        
        cursor.execute("DELETE FROM BalanceVacaciones WHERE IdBalance = ?", (id,))
        conn.commit()
        return {"mensaje": "Balance eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar balance: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

