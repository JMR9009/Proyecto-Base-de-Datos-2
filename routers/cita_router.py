from fastapi import APIRouter, HTTPException, status
from models.cita import Cita, CitaResponse
from typing import List
import pyodbc
from database import Database
from exceptions import NotFoundError, DatabaseError

router = APIRouter(prefix="/citas", tags=["citas"])


def _get_connection():
    """Obtiene una conexión a la base de datos"""
    return Database.get_connection()


def _row_to_cita_response(row) -> CitaResponse:
    """Convierte una fila de la base de datos a un modelo CitaResponse"""
    return CitaResponse(
        IdCita=row.IdCita,
        IdPaciente=row.IdPaciente,
        IdMedico=row.IdMedico,
        FechaCita=row.FechaCita,
        Motivo=row.Motivo,
        Estado=row.Estado
    )


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=dict)
def crear_cita(cita: Cita):
    """Crear una nueva cita"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Citas (IdPaciente, IdMedico, FechaCita, Motivo, Estado)
            VALUES (?, ?, ?, ?, ?)
        """, cita.IdPaciente, cita.IdMedico, cita.FechaCita, cita.Motivo, cita.Estado)
        conn.commit()
        return {"mensaje": "Cita creada exitosamente"}
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la cita: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.get("/", response_model=List[CitaResponse])
def obtener_citas():
    """Obtener todas las citas"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Citas ORDER BY FechaCita DESC")
        rows = cursor.fetchall()
        return [_row_to_cita_response(row) for row in rows]
    except pyodbc.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las citas: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=CitaResponse)
def obtener_cita(id: int):
    """Obtener una cita por ID"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Citas WHERE IdCita = ?", (id,))
        row = cursor.fetchone()
        
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cita con ID {id} no encontrada"
            )
        
        return _row_to_cita_response(row)
    except HTTPException:
        raise
    except pyodbc.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la cita: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_cita(id: int, cita: Cita):
    """Actualizar una cita existente"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Citas
            SET IdPaciente = ?, IdMedico = ?, FechaCita = ?, Motivo = ?, Estado = ?
            WHERE IdCita = ?
        """, cita.IdPaciente, cita.IdMedico, cita.FechaCita, cita.Motivo, cita.Estado, id)
        
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cita con ID {id} no encontrada"
            )
        
        conn.commit()
        return {"mensaje": "Cita actualizada exitosamente"}
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la cita: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_cita(id: int):
    """Eliminar una cita"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Citas WHERE IdCita = ?", (id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cita con ID {id} no encontrada"
            )
        
        conn.commit()
        return {"mensaje": "Cita eliminada exitosamente"}
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la cita: {str(e)}"
        )
    finally:
        if conn:
            conn.close()

