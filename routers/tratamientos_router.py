from fastapi import APIRouter, HTTPException, status
from models.diagnosticos import Tratamiento, TratamientoResponse
from typing import List
import pyodbc
from database import Database

router = APIRouter(prefix="/tratamientos", tags=["tratamientos"])


def _get_connection():
    """Obtiene una conexión a la base de datos"""
    return Database.get_connection()


def _row_to_tratamiento_response(row) -> TratamientoResponse:
    """Convierte una fila de la base de datos a un modelo TratamientoResponse"""
    return TratamientoResponse(
        IdTratamiento=row.IdTratamiento,
        IdDiagnostico=row.IdDiagnostico,
        Descripcion=row.Descripcion,
        FechaInicio=row.FechaInicio,
        FechaFin=row.FechaFin if hasattr(row, 'FechaFin') else None,
        Medicamentos=row.Medicamentos if hasattr(row, 'Medicamentos') else None
    )


@router.get("/", response_model=List[TratamientoResponse])
def obtener_tratamientos():
    """Obtener todos los tratamientos"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Tratamientos ORDER BY FechaInicio DESC")
        rows = cursor.fetchall()
        return [_row_to_tratamiento_response(row) for row in rows]
    except pyodbc.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los tratamientos: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=TratamientoResponse)
def obtener_tratamiento(id: int):
    """Obtener un tratamiento por ID"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Tratamientos WHERE IdTratamiento = ?", (id,))
        row = cursor.fetchone()
        
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tratamiento con ID {id} no encontrado"
            )
        
        return _row_to_tratamiento_response(row)
    except HTTPException:
        raise
    except pyodbc.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el tratamiento: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=dict)
def crear_tratamiento(tratamiento: Tratamiento):
    """Crear un nuevo tratamiento"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Tratamientos (IdDiagnostico, Descripcion, FechaInicio, FechaFin, Medicamentos)
            VALUES (?, ?, ?, ?, ?)
        """, (
            tratamiento.IdDiagnostico,
            tratamiento.Descripcion,
            tratamiento.FechaInicio,
            tratamiento.FechaFin,
            tratamiento.Medicamentos
        ))
        conn.commit()
        return {"mensaje": "Tratamiento creado exitosamente"}
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el tratamiento: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_tratamiento(id: int, tratamiento: Tratamiento):
    """Actualizar un tratamiento existente"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Tratamientos
            SET IdDiagnostico = ?, Descripcion = ?, FechaInicio = ?, FechaFin = ?, Medicamentos = ?
            WHERE IdTratamiento = ?
        """, (
            tratamiento.IdDiagnostico,
            tratamiento.Descripcion,
            tratamiento.FechaInicio,
            tratamiento.FechaFin,
            tratamiento.Medicamentos,
            id
        ))
        
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tratamiento con ID {id} no encontrado"
            )
        
        conn.commit()
        return {"mensaje": "Tratamiento actualizado exitosamente"}
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el tratamiento: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_tratamiento(id: int):
    """Eliminar un tratamiento"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Tratamientos WHERE IdTratamiento = ?", (id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tratamiento con ID {id} no encontrado"
            )
        
        conn.commit()
        return {"mensaje": "Tratamiento eliminado exitosamente"}
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el tratamiento: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.get("/diagnostico/{id_diagnostico}", response_model=List[TratamientoResponse])
def obtener_tratamientos_por_diagnostico(id_diagnostico: int):
    """Obtener todos los tratamientos de un diagnóstico"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM Tratamientos WHERE IdDiagnostico = ? ORDER BY FechaInicio DESC",
            (id_diagnostico,)
        )
        rows = cursor.fetchall()
        return [_row_to_tratamiento_response(row) for row in rows]
    except pyodbc.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los tratamientos: {str(e)}"
        )
    finally:
        if conn:
            conn.close()
