"""
Router para gestión de Criterios de Evaluación
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models.evaluacion_desempeno import CriterioEvaluacion, CriterioEvaluacionResponse
from database import get_db_connection
from auth import get_current_active_user
from security import safe_error_message
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/criterios-evaluacion", tags=["criterios-evaluacion"])


@router.get("/", response_model=List[CriterioEvaluacionResponse])
def obtener_criterios(current_user: dict = Depends(get_current_active_user)):
    """Obtener todos los criterios de evaluación"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM CriteriosEvaluacion ORDER BY Nombre")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener criterios: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=CriterioEvaluacionResponse)
def obtener_criterio(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener un criterio por ID"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM CriteriosEvaluacion WHERE IdCriterio = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Criterio no encontrado")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener criterio: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/activos", response_model=List[CriterioEvaluacionResponse])
def obtener_criterios_activos(current_user: dict = Depends(get_current_active_user)):
    """Obtener criterios activos"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM CriteriosEvaluacion WHERE Activo = 1 ORDER BY Nombre")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener criterios activos: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_criterio(criterio: CriterioEvaluacion, current_user: dict = Depends(get_current_active_user)):
    """Crear un nuevo criterio de evaluación"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO CriteriosEvaluacion (Nombre, Descripcion, Peso, TipoEscala, EscalaMinima, EscalaMaxima, Activo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            criterio.Nombre,
            criterio.Descripcion,
            criterio.Peso,
            criterio.TipoEscala,
            criterio.EscalaMinima,
            criterio.EscalaMaxima,
            1 if criterio.Activo else 0
        ))
        criterio_id = cursor.lastrowid
        conn.commit()
        return {"mensaje": "Criterio creado exitosamente", "IdCriterio": criterio_id}
    except Exception as e:
        logger.error(f"Error al crear criterio: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_criterio(id: int, criterio: CriterioEvaluacion, current_user: dict = Depends(get_current_active_user)):
    """Actualizar un criterio"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdCriterio FROM CriteriosEvaluacion WHERE IdCriterio = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Criterio no encontrado")
        
        cursor.execute("""
            UPDATE CriteriosEvaluacion 
            SET Nombre = ?, Descripcion = ?, Peso = ?, TipoEscala = ?, EscalaMinima = ?, EscalaMaxima = ?, Activo = ?
            WHERE IdCriterio = ?
        """, (
            criterio.Nombre,
            criterio.Descripcion,
            criterio.Peso,
            criterio.TipoEscala,
            criterio.EscalaMinima,
            criterio.EscalaMaxima,
            1 if criterio.Activo else 0,
            id
        ))
        conn.commit()
        return {"mensaje": "Criterio actualizado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar criterio: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_criterio(id: int, current_user: dict = Depends(get_current_active_user)):
    """Eliminar un criterio"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdCriterio FROM CriteriosEvaluacion WHERE IdCriterio = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Criterio no encontrado")
        
        # Verificar si tiene evaluaciones asociadas
        cursor.execute("SELECT COUNT(*) FROM CriteriosEvaluados WHERE IdCriterio = ?", (id,))
        if cursor.fetchone()[0] > 0:
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar el criterio porque tiene evaluaciones asociadas"
            )
        
        cursor.execute("DELETE FROM CriteriosEvaluacion WHERE IdCriterio = ?", (id,))
        conn.commit()
        return {"mensaje": "Criterio eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar criterio: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

