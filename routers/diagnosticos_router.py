from fastapi import APIRouter, HTTPException, status
from models.diagnosticos import Diagnostico, DiagnosticoResponse
from typing import List
import pyodbc
from database import Database

router = APIRouter(prefix="/diagnosticos", tags=["diagnosticos"])


def _get_connection():
    """Obtiene una conexión a la base de datos"""
    return Database.get_connection()


def _row_to_diagnostico_response(row) -> DiagnosticoResponse:
    """Convierte una fila de la base de datos a un modelo DiagnosticoResponse"""
    return DiagnosticoResponse(
        IdDiagnostico=row.IdDiagnostico,
        IdPaciente=row.IdPaciente,
        Descripcion=row.Descripcion,
        FechaDiagnostico=row.FechaDiagnostico,
        CodigoICD10=row.CodigoICD10 if hasattr(row, 'CodigoICD10') else None
    )


@router.get("/", response_model=List[DiagnosticoResponse])
def obtener_diagnosticos():
    """Obtener todos los diagnósticos"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Diagnosticos ORDER BY FechaDiagnostico DESC")
        rows = cursor.fetchall()
        return [_row_to_diagnostico_response(row) for row in rows]
    except pyodbc.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los diagnósticos: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=DiagnosticoResponse)
def obtener_diagnostico(id: int):
    """Obtener un diagnóstico por ID"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Diagnosticos WHERE IdDiagnostico = ?", (id,))
        row = cursor.fetchone()
        
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnóstico con ID {id} no encontrado"
            )
        
        return _row_to_diagnostico_response(row)
    except HTTPException:
        raise
    except pyodbc.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el diagnóstico: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=dict)
def crear_diagnostico(diagnostico: Diagnostico):
    """Crear un nuevo diagnóstico"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Diagnosticos (IdPaciente, Descripcion, FechaDiagnostico, CodigoICD10)
            VALUES (?, ?, ?, ?)
        """, (
            diagnostico.IdPaciente,
            diagnostico.Descripcion,
            diagnostico.FechaDiagnostico,
            diagnostico.CodigoICD10
        ))
        conn.commit()
        return {"mensaje": "Diagnóstico creado exitosamente"}
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el diagnóstico: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_diagnostico(id: int, diagnostico: Diagnostico):
    """Actualizar un diagnóstico existente"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Diagnosticos
            SET IdPaciente = ?, Descripcion = ?, FechaDiagnostico = ?, CodigoICD10 = ?
            WHERE IdDiagnostico = ?
        """, (
            diagnostico.IdPaciente,
            diagnostico.Descripcion,
            diagnostico.FechaDiagnostico,
            diagnostico.CodigoICD10,
            id
        ))
        
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnóstico con ID {id} no encontrado"
            )
        
        conn.commit()
        return {"mensaje": "Diagnóstico actualizado exitosamente"}
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el diagnóstico: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_diagnostico(id: int):
    """Eliminar un diagnóstico"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Diagnosticos WHERE IdDiagnostico = ?", (id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnóstico con ID {id} no encontrado"
            )
        
        conn.commit()
        return {"mensaje": "Diagnóstico eliminado exitosamente"}
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el diagnóstico: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.get("/paciente/{id_paciente}", response_model=List[DiagnosticoResponse])
def obtener_diagnosticos_por_paciente(id_paciente: int):
    """Obtener todos los diagnósticos de un paciente"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM Diagnosticos WHERE IdPaciente = ? ORDER BY FechaDiagnostico DESC",
            (id_paciente,)
        )
        rows = cursor.fetchall()
        return [_row_to_diagnostico_response(row) for row in rows]
    except pyodbc.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los diagnósticos: {str(e)}"
        )
    finally:
        if conn:
            conn.close()
