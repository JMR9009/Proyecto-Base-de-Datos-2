"""
Router para gestión de Médicos
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models.medico import Medico, MedicoResponse
from database import get_db_connection
from auth import get_current_active_user
from security import safe_error_message
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/medicos", tags=["medicos"])


@router.get("/", response_model=List[MedicoResponse])
def obtener_medicos(current_user: dict = Depends(get_current_active_user)):
    """Obtener todos los médicos"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Medicos ORDER BY Apellido, Nombre")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener médicos: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=MedicoResponse)
def obtener_medico(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener un médico por ID"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Medicos WHERE IdMedico = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Médico no encontrado")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener médico: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_medico(medico: Medico, current_user: dict = Depends(get_current_active_user)):
    """Crear un nuevo médico"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Medicos (Nombre, Apellido, Especialidad, Telefono, Email)
            VALUES (?, ?, ?, ?, ?)
        """, (
            medico.Nombre,
            medico.Apellido,
            medico.Especialidad,
            medico.Telefono,
            medico.Email
        ))
        medico_id = cursor.lastrowid
        conn.commit()
        return {"mensaje": "Médico creado exitosamente", "IdMedico": medico_id}
    except Exception as e:
        logger.error(f"Error al crear médico: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_medico(id: int, medico: Medico, current_user: dict = Depends(get_current_active_user)):
    """Actualizar un médico"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que existe
        cursor.execute("SELECT IdMedico FROM Medicos WHERE IdMedico = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Médico no encontrado")
        
        cursor.execute("""
            UPDATE Medicos 
            SET Nombre = ?, Apellido = ?, Especialidad = ?, Telefono = ?, Email = ?
            WHERE IdMedico = ?
        """, (
            medico.Nombre,
            medico.Apellido,
            medico.Especialidad,
            medico.Telefono,
            medico.Email,
            id
        ))
        conn.commit()
        return {"mensaje": "Médico actualizado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar médico: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_medico(id: int, current_user: dict = Depends(get_current_active_user)):
    """Eliminar un médico"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que existe
        cursor.execute("SELECT IdMedico FROM Medicos WHERE IdMedico = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Médico no encontrado")
        
        # Verificar si tiene citas asociadas
        cursor.execute("SELECT COUNT(*) FROM Citas WHERE IdMedico = ?", (id,))
        if cursor.fetchone()[0] > 0:
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar el médico porque tiene citas asociadas"
            )
        
        cursor.execute("DELETE FROM Medicos WHERE IdMedico = ?", (id,))
        conn.commit()
        return {"mensaje": "Médico eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar médico: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

