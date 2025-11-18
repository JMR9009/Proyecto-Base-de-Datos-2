from fastapi import APIRouter, HTTPException, Depends
from models.asistencia import Asistencia
from pydantic import BaseModel
from typing import List, Optional
from database import get_db_connection
from security import sanitize_string, safe_error_message
from auth import get_current_active_user
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/asistencia", tags=["asistencia"])


class AsistenciaResponse(BaseModel):
    IdAsistencia: Optional[int]
    IdEmpleado: int
    Fecha: str
    HoraEntrada: Optional[str]
    HoraSalida: Optional[str]
    TipoRegistro: str
    TipoRegistroOrigen: Optional[str]
    Estado: str
    Observaciones: Optional[str]
    Justificacion: Optional[str]
    HorasTrabajadas: Optional[float]
    Latitud: Optional[float]
    Longitud: Optional[float]


def validate_empleado_exists(cursor, id_empleado: int):
    """Validar que el empleado exista"""
    cursor.execute("SELECT COUNT(*) FROM Empleados WHERE IdEmpleado = ?", (id_empleado,))
    if cursor.fetchone()[0] == 0:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")


@router.post("/", response_model=dict)
def crear_asistencia(asistencia: Asistencia, current_user: dict = Depends(get_current_active_user)):
    """Crear un nuevo registro de asistencia"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validar que el empleado exista
        validate_empleado_exists(cursor, asistencia.IdEmpleado)
        
        cursor.execute("""
            INSERT INTO Asistencia (
                IdEmpleado, Fecha, HoraEntrada, HoraSalida, TipoRegistro,
                TipoRegistroOrigen, Estado, Observaciones, Justificacion,
                HorasTrabajadas, Latitud, Longitud
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            asistencia.IdEmpleado,
            asistencia.Fecha,
            asistencia.HoraEntrada,
            asistencia.HoraSalida,
            asistencia.TipoRegistro,
            asistencia.TipoRegistroOrigen,
            asistencia.Estado,
            asistencia.Observaciones,
            asistencia.Justificacion,
            asistencia.HorasTrabajadas,
            asistencia.Latitud,
            asistencia.Longitud
        ))
        conn.commit()
        asistencia_id = cursor.lastrowid
        logger.info(f"Asistencia creada: ID {asistencia_id}")
        return {"mensaje": "Asistencia registrada exitosamente", "IdAsistencia": asistencia_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear asistencia: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/entrada", response_model=dict)
def registrar_entrada(asistencia: Asistencia, current_user: dict = Depends(get_current_active_user)):
    """Registrar entrada de un empleado"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        validate_empleado_exists(cursor, asistencia.IdEmpleado)
        
        # Verificar si ya existe un registro de entrada para este día
        cursor.execute("""
            SELECT IdAsistencia FROM Asistencia
            WHERE IdEmpleado = ? AND Fecha = ? AND HoraEntrada IS NOT NULL
        """, (asistencia.IdEmpleado, asistencia.Fecha))
        existing = cursor.fetchone()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Ya existe un registro de entrada para este empleado en esta fecha"
            )
        
        cursor.execute("""
            INSERT INTO Asistencia (
                IdEmpleado, Fecha, HoraEntrada, TipoRegistro,
                TipoRegistroOrigen, Estado, Observaciones, Justificacion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            asistencia.IdEmpleado,
            asistencia.Fecha,
            asistencia.HoraEntrada,
            'entrada',
            asistencia.TipoRegistroOrigen or 'manual',
            asistencia.Estado or 'presente',
            asistencia.Observaciones,
            asistencia.Justificacion
        ))
        conn.commit()
        asistencia_id = cursor.lastrowid
        logger.info(f"Entrada registrada: ID {asistencia_id}")
        return {"mensaje": "Entrada registrada exitosamente", "IdAsistencia": asistencia_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al registrar entrada: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}/salida", response_model=dict)
def registrar_salida(id: int, datos_salida: dict, current_user: dict = Depends(get_current_active_user)):
    """Registrar salida de un empleado"""
    if id <= 0:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener el registro de asistencia
        cursor.execute("SELECT * FROM Asistencia WHERE IdAsistencia = ?", (id,))
        registro = cursor.fetchone()
        
        if registro is None:
            raise HTTPException(status_code=404, detail="Registro de asistencia no encontrado")
        
        if registro["HoraSalida"]:
            raise HTTPException(
                status_code=400,
                detail="Ya existe un registro de salida para este día"
            )
        
        hora_salida = datos_salida.get("HoraSalida")
        horas_trabajadas = datos_salida.get("HorasTrabajadas")
        
        # Calcular horas trabajadas si no se proporciona
        if not horas_trabajadas and registro["HoraEntrada"] and hora_salida:
            entrada = registro["HoraEntrada"].split(':')
            salida = hora_salida.split(':')
            minutos_entrada = int(entrada[0]) * 60 + int(entrada[1])
            minutos_salida = int(salida[0]) * 60 + int(salida[1])
            horas_trabajadas = (minutos_salida - minutos_entrada) / 60.0
        
        cursor.execute("""
            UPDATE Asistencia
            SET HoraSalida = ?, HorasTrabajadas = ?, TipoRegistro = ?
            WHERE IdAsistencia = ?
        """, (hora_salida, horas_trabajadas, 'salida', id))
        
        conn.commit()
        logger.info(f"Salida registrada: ID {id}")
        return {"mensaje": "Salida registrada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al registrar salida {id}: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/", response_model=List[AsistenciaResponse])
def obtener_asistencias(current_user: dict = Depends(get_current_active_user)):
    """Obtener todos los registros de asistencia"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Asistencia ORDER BY Fecha DESC, HoraEntrada DESC")
        rows = cursor.fetchall()
        return [
            {
                "IdAsistencia": row["IdAsistencia"],
                "IdEmpleado": row["IdEmpleado"],
                "Fecha": row["Fecha"],
                "HoraEntrada": row["HoraEntrada"],
                "HoraSalida": row["HoraSalida"],
                "TipoRegistro": row["TipoRegistro"],
                "TipoRegistroOrigen": row["TipoRegistroOrigen"],
                "Estado": row["Estado"],
                "Observaciones": row["Observaciones"],
                "Justificacion": row["Justificacion"],
                "HorasTrabajadas": row["HorasTrabajadas"],
                "Latitud": row["Latitud"],
                "Longitud": row["Longitud"]
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error al obtener asistencias: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=AsistenciaResponse)
def obtener_asistencia(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener un registro de asistencia por ID"""
    if id <= 0:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Asistencia WHERE IdAsistencia = ?", (id,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Registro de asistencia no encontrado")
        return {
            "IdAsistencia": row["IdAsistencia"],
            "IdEmpleado": row["IdEmpleado"],
            "Fecha": row["Fecha"],
            "HoraEntrada": row["HoraEntrada"],
            "HoraSalida": row["HoraSalida"],
            "TipoRegistro": row["TipoRegistro"],
            "TipoRegistroOrigen": row["TipoRegistroOrigen"],
            "Estado": row["Estado"],
            "Observaciones": row["Observaciones"],
            "Justificacion": row["Justificacion"],
            "HorasTrabajadas": row["HorasTrabajadas"],
            "Latitud": row["Latitud"],
            "Longitud": row["Longitud"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener asistencia {id}: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/empleado/{id_empleado}", response_model=List[AsistenciaResponse])
def obtener_asistencias_por_empleado(id_empleado: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener todos los registros de asistencia de un empleado"""
    if id_empleado <= 0:
        raise HTTPException(status_code=400, detail="ID de empleado inválido")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM Asistencia 
            WHERE IdEmpleado = ? 
            ORDER BY Fecha DESC, HoraEntrada DESC
        """, (id_empleado,))
        rows = cursor.fetchall()
        return [
            {
                "IdAsistencia": row["IdAsistencia"],
                "IdEmpleado": row["IdEmpleado"],
                "Fecha": row["Fecha"],
                "HoraEntrada": row["HoraEntrada"],
                "HoraSalida": row["HoraSalida"],
                "TipoRegistro": row["TipoRegistro"],
                "TipoRegistroOrigen": row["TipoRegistroOrigen"],
                "Estado": row["Estado"],
                "Observaciones": row["Observaciones"],
                "Justificacion": row["Justificacion"],
                "HorasTrabajadas": row["HorasTrabajadas"],
                "Latitud": row["Latitud"],
                "Longitud": row["Longitud"]
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error al obtener asistencias del empleado {id_empleado}: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/fecha/{fecha}", response_model=List[AsistenciaResponse])
def obtener_asistencias_por_fecha(fecha: str, current_user: dict = Depends(get_current_active_user)):
    """Obtener todos los registros de asistencia de una fecha específica"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM Asistencia 
            WHERE Fecha = ? 
            ORDER BY HoraEntrada DESC
        """, (fecha,))
        rows = cursor.fetchall()
        return [
            {
                "IdAsistencia": row["IdAsistencia"],
                "IdEmpleado": row["IdEmpleado"],
                "Fecha": row["Fecha"],
                "HoraEntrada": row["HoraEntrada"],
                "HoraSalida": row["HoraSalida"],
                "TipoRegistro": row["TipoRegistro"],
                "TipoRegistroOrigen": row["TipoRegistroOrigen"],
                "Estado": row["Estado"],
                "Observaciones": row["Observaciones"],
                "Justificacion": row["Justificacion"],
                "HorasTrabajadas": row["HorasTrabajadas"],
                "Latitud": row["Latitud"],
                "Longitud": row["Longitud"]
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error al obtener asistencias de la fecha {fecha}: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/rango", response_model=List[AsistenciaResponse])
def obtener_asistencias_por_rango(inicio: str, fin: str, current_user: dict = Depends(get_current_active_user)):
    """Obtener registros de asistencia en un rango de fechas"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM Asistencia 
            WHERE Fecha >= ? AND Fecha <= ?
            ORDER BY Fecha DESC, HoraEntrada DESC
        """, (inicio, fin))
        rows = cursor.fetchall()
        return [
            {
                "IdAsistencia": row["IdAsistencia"],
                "IdEmpleado": row["IdEmpleado"],
                "Fecha": row["Fecha"],
                "HoraEntrada": row["HoraEntrada"],
                "HoraSalida": row["HoraSalida"],
                "TipoRegistro": row["TipoRegistro"],
                "TipoRegistroOrigen": row["TipoRegistroOrigen"],
                "Estado": row["Estado"],
                "Observaciones": row["Observaciones"],
                "Justificacion": row["Justificacion"],
                "HorasTrabajadas": row["HorasTrabajadas"],
                "Latitud": row["Latitud"],
                "Longitud": row["Longitud"]
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error al obtener asistencias del rango {inicio} a {fin}: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_asistencia(id: int, asistencia: dict, current_user: dict = Depends(get_current_active_user)):
    """Actualizar un registro de asistencia existente"""
    if id <= 0:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que el registro existe
        cursor.execute("SELECT * FROM Asistencia WHERE IdAsistencia = ?", (id,))
        registro_existente = cursor.fetchone()
        if registro_existente is None:
            raise HTTPException(status_code=404, detail="Registro de asistencia no encontrado")
        
        # Validar empleado si se proporciona
        if "IdEmpleado" in asistencia:
            validate_empleado_exists(cursor, asistencia["IdEmpleado"])
        
        # Construir query de actualización dinámicamente
        campos_actualizar = []
        valores = []
        
        campos_permitidos = [
            "IdEmpleado", "Fecha", "HoraEntrada", "HoraSalida",
            "TipoRegistro", "TipoRegistroOrigen", "Estado",
            "Observaciones", "Justificacion", "HorasTrabajadas",
            "Latitud", "Longitud"
        ]
        
        for campo in campos_permitidos:
            if campo in asistencia:
                campos_actualizar.append(f"{campo} = ?")
                valores.append(asistencia[campo])
        
        if not campos_actualizar:
            raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")
        
        valores.append(id)
        query = f"UPDATE Asistencia SET {', '.join(campos_actualizar)} WHERE IdAsistencia = ?"
        
        cursor.execute(query, valores)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Registro de asistencia no encontrado")
        
        conn.commit()
        logger.info(f"Asistencia actualizada: ID {id}")
        return {"mensaje": "Asistencia actualizada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar asistencia {id}: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_asistencia(id: int, current_user: dict = Depends(get_current_active_user)):
    """Eliminar un registro de asistencia"""
    if id <= 0:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Asistencia WHERE IdAsistencia = ?", (id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Registro de asistencia no encontrado")
        conn.commit()
        logger.info(f"Asistencia eliminada: ID {id}")
        return {"mensaje": "Registro de asistencia eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar asistencia {id}: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

