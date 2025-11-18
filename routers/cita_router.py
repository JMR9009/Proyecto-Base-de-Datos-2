from fastapi import APIRouter, HTTPException
from models.cita import Cita
from pydantic import BaseModel, validator, Field
from typing import List
from database import get_db_connection
from security import sanitize_string, safe_error_message
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/citas", tags=["citas"])


class CitaResponse(BaseModel):
    IdCita: int
    IdPaciente: int
    IdMedico: int
    FechaHora: str  # Cambiado a FechaHora para coincidir con el frontend
    Motivo: str
    Estado: str


def validate_references(cursor, id_paciente: int, id_medico: int):
    """Validar que paciente y médico existan"""
    cursor.execute("SELECT COUNT(*) FROM Pacientes WHERE IdPaciente = ?", (id_paciente,))
    if cursor.fetchone()[0] == 0:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    cursor.execute("SELECT COUNT(*) FROM Medicos WHERE IdMedico = ?", (id_medico,))
    if cursor.fetchone()[0] == 0:
        raise HTTPException(status_code=404, detail="Médico no encontrado")

@router.post("/", response_model=dict)
def crear_cita(cita: Cita):
    """Crear una nueva cita"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validar que paciente y médico existan
        validate_references(cursor, cita.IdPaciente, cita.IdMedico)
        
        cursor.execute("""
            INSERT INTO Citas (IdPaciente, IdMedico, FechaCita, Motivo, Estado)
            VALUES (?, ?, ?, ?, ?)
        """, (cita.IdPaciente, cita.IdMedico, cita.FechaHora, cita.Motivo, cita.Estado))
        conn.commit()
        cita_id = cursor.lastrowid
        logger.info(f"Cita creada: ID {cita_id}")
        return {"mensaje": "Cita creada exitosamente", "IdCita": cita_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear cita: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/", response_model=List[CitaResponse])
def obtener_citas():
    """Obtener todas las citas"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Citas")
        rows = cursor.fetchall()
        return [
            {
                "IdCita": row["IdCita"],
                "IdPaciente": row["IdPaciente"],
                "IdMedico": row["IdMedico"],
                "FechaHora": str(row["FechaCita"]) if row["FechaCita"] else None,
                "Motivo": row["Motivo"],
                "Estado": row["Estado"]
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error al obtener citas: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=CitaResponse)
def obtener_cita(id: int):
    """Obtener una cita por ID"""
    if id <= 0:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Citas WHERE IdCita = ?", (id,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        return {
            "IdCita": row["IdCita"],
            "IdPaciente": row["IdPaciente"],
            "IdMedico": row["IdMedico"],
            "FechaHora": str(row["FechaCita"]) if row["FechaCita"] else None,
            "Motivo": row["Motivo"],
            "Estado": row["Estado"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener cita {id}: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_cita(id: int, cita: Cita):
    """Actualizar una cita existente"""
    if id <= 0:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validar que paciente y médico existan
        validate_references(cursor, cita.IdPaciente, cita.IdMedico)
        
        cursor.execute("""
            UPDATE Citas
            SET IdPaciente = ?, IdMedico = ?, FechaCita = ?, Motivo = ?, Estado = ?
            WHERE IdCita = ?
        """, (cita.IdPaciente, cita.IdMedico, cita.FechaHora, cita.Motivo, cita.Estado, id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        conn.commit()
        logger.info(f"Cita actualizada: ID {id}")
        return {"mensaje": "Cita actualizada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar cita {id}: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_cita(id: int):
    """Eliminar una cita"""
    if id <= 0:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Citas WHERE IdCita = ?", (id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        conn.commit()
        logger.info(f"Cita eliminada: ID {id}")
        return {"mensaje": "Cita eliminada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar cita {id}: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

