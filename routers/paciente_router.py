"""
Router para gestión de Pacientes
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models.paciente import Paciente, PacienteResponse
from database import get_db_connection
from auth import get_current_active_user
from security import safe_error_message
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/pacientes", tags=["pacientes"])


@router.get("/", response_model=List[PacienteResponse])
def obtener_pacientes(current_user: dict = Depends(get_current_active_user)):
    """Obtener todos los pacientes"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Pacientes ORDER BY Apellido, Nombre")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener pacientes: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=PacienteResponse)
def obtener_paciente(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener un paciente por ID"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Pacientes WHERE IdPaciente = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener paciente: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_paciente(paciente: Paciente, current_user: dict = Depends(get_current_active_user)):
    """Crear un nuevo paciente"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Pacientes (Nombre, Apellido, FechaNacimiento, Genero, Telefono, Email, Direccion)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            paciente.Nombre,
            paciente.Apellido,
            paciente.FechaNacimiento,
            paciente.Genero,
            paciente.Telefono,
            paciente.Email,
            paciente.Direccion
        ))
        paciente_id = cursor.lastrowid
        conn.commit()
        return {"mensaje": "Paciente creado exitosamente", "IdPaciente": paciente_id}
    except Exception as e:
        logger.error(f"Error al crear paciente: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_paciente(id: int, paciente: Paciente, current_user: dict = Depends(get_current_active_user)):
    """Actualizar un paciente"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que existe
        cursor.execute("SELECT IdPaciente FROM Pacientes WHERE IdPaciente = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        cursor.execute("""
            UPDATE Pacientes 
            SET Nombre = ?, Apellido = ?, FechaNacimiento = ?, Genero = ?, 
                Telefono = ?, Email = ?, Direccion = ?
            WHERE IdPaciente = ?
        """, (
            paciente.Nombre,
            paciente.Apellido,
            paciente.FechaNacimiento,
            paciente.Genero,
            paciente.Telefono,
            paciente.Email,
            paciente.Direccion,
            id
        ))
        conn.commit()
        return {"mensaje": "Paciente actualizado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar paciente: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_paciente(id: int, current_user: dict = Depends(get_current_active_user)):
    """Eliminar un paciente"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que existe
        cursor.execute("SELECT IdPaciente FROM Pacientes WHERE IdPaciente = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        # Verificar si tiene citas asociadas
        cursor.execute("SELECT COUNT(*) FROM Citas WHERE IdPaciente = ?", (id,))
        if cursor.fetchone()[0] > 0:
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar el paciente porque tiene citas asociadas"
            )
        
        cursor.execute("DELETE FROM Pacientes WHERE IdPaciente = ?", (id,))
        conn.commit()
        return {"mensaje": "Paciente eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar paciente: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

