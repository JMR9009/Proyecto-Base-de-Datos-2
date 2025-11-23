from fastapi import APIRouter, HTTPException, status
from models.medico import Medico, MedicoResponse
from typing import List
import pyodbc

router = APIRouter(prefix="/medicos", tags=["medicos"])

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=MANUEL\\MSSQL2022;"
    "DATABASE=ClinicaMedica;"
    "Trusted_Connection=yes;"
)


def _get_connection():
    """Obtiene una conexión a la base de datos"""
    return pyodbc.connect(CONNECTION_STRING)


def _row_to_medico_response(row) -> MedicoResponse:
    """Convierte una fila de la base de datos a un modelo MedicoResponse"""
    return MedicoResponse(
        IdMedico=row.IdMedico,
        Nombre=row.Nombre,
        Apellido=row.Apellido,
        Especialidad=row.Especialidad,
        Telefono=row.Telefono,
        Email=row.Email
    )


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=dict)
def crear_medico(medico: Medico):
    """Crear un nuevo médico"""
    conn = None
    try:
        conn = _get_connection()
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
        conn.commit()
        return {"mensaje": "Médico creado exitosamente"}
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el médico: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.get("/", response_model=List[MedicoResponse])
def obtener_medicos():
    """Obtener todos los médicos"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Medicos ORDER BY Apellido, Nombre")
        rows = cursor.fetchall()
        return [_row_to_medico_response(row) for row in rows]
    except pyodbc.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los médicos: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=MedicoResponse)
def obtener_medico(id: int):
    """Obtener un médico por ID"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Medicos WHERE IdMedico = ?", (id,))
        row = cursor.fetchone()
        
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Médico con ID {id} no encontrado"
            )
        
        return _row_to_medico_response(row)
    except HTTPException:
        raise
    except pyodbc.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el médico: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_medico(id: int, medico: Medico):
    """Actualizar un médico existente"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
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
        
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Médico con ID {id} no encontrado"
            )
        
        conn.commit()
        return {"mensaje": "Médico actualizado exitosamente"}
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el médico: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_medico(id: int):
    """Eliminar un médico"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Medicos WHERE IdMedico = ?", (id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Médico con ID {id} no encontrado"
            )
        
        conn.commit()
        return {"mensaje": "Médico eliminado exitosamente"}
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el médico: {str(e)}"
        )
    finally:
        if conn:
            conn.close()

