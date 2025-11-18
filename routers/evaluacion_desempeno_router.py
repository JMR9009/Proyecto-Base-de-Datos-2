"""
Router para gestión de Evaluaciones de Desempeño
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models.evaluacion_desempeno import EvaluacionDesempeno, EvaluacionDesempenoResponse
from database import get_db_connection
from auth import get_current_active_user
from security import safe_error_message
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/evaluaciones-desempeno", tags=["evaluaciones-desempeno"])


def validate_empleado_exists(cursor, id_empleado: int):
    """Validar que el empleado existe"""
    cursor.execute("SELECT IdEmpleado FROM Empleados WHERE IdEmpleado = ?", (id_empleado,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Empleado no encontrado")


@router.get("/", response_model=List[EvaluacionDesempenoResponse])
def obtener_evaluaciones(current_user: dict = Depends(get_current_active_user)):
    """Obtener todas las evaluaciones de desempeño"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM EvaluacionesDesempeno ORDER BY FechaEvaluacion DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener evaluaciones: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=EvaluacionDesempenoResponse)
def obtener_evaluacion(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener una evaluación por ID"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM EvaluacionesDesempeno WHERE IdEvaluacion = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Evaluación no encontrada")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener evaluación: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/empleado/{id_empleado}", response_model=List[EvaluacionDesempenoResponse])
def obtener_evaluaciones_por_empleado(id_empleado: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener evaluaciones por empleado"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        validate_empleado_exists(cursor, id_empleado)
        cursor.execute("SELECT * FROM EvaluacionesDesempeno WHERE IdEmpleado = ? ORDER BY FechaEvaluacion DESC", (id_empleado,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener evaluaciones por empleado: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/evaluador/{id_evaluador}", response_model=List[EvaluacionDesempenoResponse])
def obtener_evaluaciones_por_evaluador(id_evaluador: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener evaluaciones por evaluador"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM EvaluacionesDesempeno WHERE IdEvaluador = ? ORDER BY FechaEvaluacion DESC", (id_evaluador,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener evaluaciones por evaluador: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/periodo/{periodo}", response_model=List[EvaluacionDesempenoResponse])
def obtener_evaluaciones_por_periodo(periodo: str, current_user: dict = Depends(get_current_active_user)):
    """Obtener evaluaciones por período"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM EvaluacionesDesempeno WHERE Periodo = ? ORDER BY FechaEvaluacion DESC", (periodo,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener evaluaciones por período: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/estado/{estado}", response_model=List[EvaluacionDesempenoResponse])
def obtener_evaluaciones_por_estado(estado: str, current_user: dict = Depends(get_current_active_user)):
    """Obtener evaluaciones por estado"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM EvaluacionesDesempeno WHERE Estado = ? ORDER BY FechaEvaluacion DESC", (estado,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener evaluaciones por estado: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_evaluacion(evaluacion: EvaluacionDesempeno, current_user: dict = Depends(get_current_active_user)):
    """Crear una nueva evaluación de desempeño"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        validate_empleado_exists(cursor, evaluacion.IdEmpleado)
        
        if evaluacion.IdEvaluador:
            validate_empleado_exists(cursor, evaluacion.IdEvaluador)
        
        cursor.execute("""
            INSERT INTO EvaluacionesDesempeno (IdEmpleado, IdEvaluador, TipoEvaluacion, Periodo, FechaEvaluacion,
                                               FechaInicioPeriodo, FechaFinPeriodo, Estado, CalificacionFinal,
                                               Fortalezas, AreasMejora, ComentariosEvaluador, ComentariosEmpleado,
                                               PlanDesarrollo, FirmaEvaluador, FirmaEmpleado, FechaFirmaEvaluador, FechaFirmaEmpleado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            evaluacion.IdEmpleado,
            evaluacion.IdEvaluador,
            evaluacion.TipoEvaluacion,
            evaluacion.Periodo,
            evaluacion.FechaEvaluacion,
            evaluacion.FechaInicioPeriodo,
            evaluacion.FechaFinPeriodo,
            evaluacion.Estado,
            evaluacion.CalificacionFinal,
            evaluacion.Fortalezas,
            evaluacion.AreasMejora,
            evaluacion.ComentariosEvaluador,
            evaluacion.ComentariosEmpleado,
            evaluacion.PlanDesarrollo,
            evaluacion.FirmaEvaluador,
            evaluacion.FirmaEmpleado,
            evaluacion.FechaFirmaEvaluador,
            evaluacion.FechaFirmaEmpleado
        ))
        evaluacion_id = cursor.lastrowid
        
        # Insertar criterios evaluados si existen
        if evaluacion.CriteriosEvaluados:
            for criterio in evaluacion.CriteriosEvaluados:
                cursor.execute("""
                    INSERT INTO CriteriosEvaluados (IdEvaluacion, IdCriterio, Calificacion, Comentarios, Evidencias)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    evaluacion_id,
                    criterio.IdCriterio,
                    criterio.Calificacion,
                    criterio.Comentarios,
                    criterio.Evidencias
                ))
        
        conn.commit()
        return {"mensaje": "Evaluación creada exitosamente", "IdEvaluacion": evaluacion_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear evaluación: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_evaluacion(id: int, evaluacion: EvaluacionDesempeno, current_user: dict = Depends(get_current_active_user)):
    """Actualizar una evaluación"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdEvaluacion FROM EvaluacionesDesempeno WHERE IdEvaluacion = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Evaluación no encontrada")
        
        validate_empleado_exists(cursor, evaluacion.IdEmpleado)
        if evaluacion.IdEvaluador:
            validate_empleado_exists(cursor, evaluacion.IdEvaluador)
        
        cursor.execute("""
            UPDATE EvaluacionesDesempeno 
            SET IdEmpleado = ?, IdEvaluador = ?, TipoEvaluacion = ?, Periodo = ?, FechaEvaluacion = ?,
                FechaInicioPeriodo = ?, FechaFinPeriodo = ?, Estado = ?, CalificacionFinal = ?,
                Fortalezas = ?, AreasMejora = ?, ComentariosEvaluador = ?, ComentariosEmpleado = ?,
                PlanDesarrollo = ?, FirmaEvaluador = ?, FirmaEmpleado = ?, FechaFirmaEvaluador = ?, FechaFirmaEmpleado = ?
            WHERE IdEvaluacion = ?
        """, (
            evaluacion.IdEmpleado,
            evaluacion.IdEvaluador,
            evaluacion.TipoEvaluacion,
            evaluacion.Periodo,
            evaluacion.FechaEvaluacion,
            evaluacion.FechaInicioPeriodo,
            evaluacion.FechaFinPeriodo,
            evaluacion.Estado,
            evaluacion.CalificacionFinal,
            evaluacion.Fortalezas,
            evaluacion.AreasMejora,
            evaluacion.ComentariosEvaluador,
            evaluacion.ComentariosEmpleado,
            evaluacion.PlanDesarrollo,
            evaluacion.FirmaEvaluador,
            evaluacion.FirmaEmpleado,
            evaluacion.FechaFirmaEvaluador,
            evaluacion.FechaFirmaEmpleado,
            id
        ))
        conn.commit()
        return {"mensaje": "Evaluación actualizada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar evaluación: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}/completar", response_model=dict)
def completar_evaluacion(id: int, evaluacion: EvaluacionDesempeno, current_user: dict = Depends(get_current_active_user)):
    """Completar una evaluación de desempeño"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdEvaluacion FROM EvaluacionesDesempeno WHERE IdEvaluacion = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Evaluación no encontrada")
        
        cursor.execute("""
            UPDATE EvaluacionesDesempeno 
            SET Estado = 'completada', CalificacionFinal = ?, Fortalezas = ?, AreasMejora = ?,
                ComentariosEvaluador = ?, ComentariosEmpleado = ?, PlanDesarrollo = ?
            WHERE IdEvaluacion = ?
        """, (
            evaluacion.CalificacionFinal,
            evaluacion.Fortalezas,
            evaluacion.AreasMejora,
            evaluacion.ComentariosEvaluador,
            evaluacion.ComentariosEmpleado,
            evaluacion.PlanDesarrollo,
            id
        ))
        conn.commit()
        return {"mensaje": "Evaluación completada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al completar evaluación: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_evaluacion(id: int, current_user: dict = Depends(get_current_active_user)):
    """Eliminar una evaluación"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdEvaluacion FROM EvaluacionesDesempeno WHERE IdEvaluacion = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Evaluación no encontrada")
        
        # Eliminar criterios evaluados asociados
        cursor.execute("DELETE FROM CriteriosEvaluados WHERE IdEvaluacion = ?", (id,))
        
        cursor.execute("DELETE FROM EvaluacionesDesempeno WHERE IdEvaluacion = ?", (id,))
        conn.commit()
        return {"mensaje": "Evaluación eliminada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar evaluación: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

