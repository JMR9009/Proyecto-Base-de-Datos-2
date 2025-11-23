from fastapi import APIRouter, HTTPException, status
from models.paciente import Paciente, PacienteResponse
from typing import List
import pyodbc

router = APIRouter(prefix="/pacientes", tags=["pacientes"])

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=MANUEL\\MSSQL2022;"
    "DATABASE=ClinicaMedica;"
    "Trusted_Connection=yes;"
)


def _get_connection():
    """Obtiene una conexión a la base de datos"""
    return pyodbc.connect(CONNECTION_STRING)


def _row_to_paciente_response(row) -> PacienteResponse:
    """Convierte una fila de la base de datos a un modelo PacienteResponse"""
    return PacienteResponse(
        IdPaciente=row.IdPaciente,
        Nombre=row.Nombre,
        Apellido=row.Apellido,
        FechaNacimiento=row.FechaNacimiento,
        Sexo=row.Sexo,
        Telefono=row.Telefono,
        Direccion=row.Direccion,
        Email=row.Email
    )


@router.get("/", response_model=List[PacienteResponse])
def obtener_pacientes():
    """Obtener todos los pacientes"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Pacientes ORDER BY Apellido, Nombre")
        rows = cursor.fetchall()
        return [_row_to_paciente_response(row) for row in rows]
    except pyodbc.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los pacientes: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=PacienteResponse)
def obtener_paciente(id: int):
    """Obtener un paciente por ID"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Pacientes WHERE IdPaciente = ?", (id,))
        row = cursor.fetchone()
        
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente con ID {id} no encontrado"
            )
        
        return _row_to_paciente_response(row)
    except HTTPException:
        raise
    except pyodbc.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el paciente: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=dict)
def crear_paciente(paciente: Paciente):
    """Crear un nuevo paciente"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Pacientes (Nombre, Apellido, FechaNacimiento, Sexo, Telefono, Direccion, Email)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            paciente.Nombre,
            paciente.Apellido,
            paciente.FechaNacimiento,
            paciente.Sexo,
            paciente.Telefono,
            paciente.Direccion,
            paciente.Email
        ))
        conn.commit()
        return {"mensaje": "Paciente creado exitosamente"}
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el paciente: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.post("/bulk", status_code=status.HTTP_201_CREATED, response_model=dict)
def crear_pacientes_multiples(pacientes: List[Paciente]):
    """Crear múltiples pacientes en una sola operación"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        
        for paciente in pacientes:
            cursor.execute("""
                INSERT INTO Pacientes (Nombre, Apellido, FechaNacimiento, Sexo, Telefono, Direccion, Email)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                paciente.Nombre,
                paciente.Apellido,
                paciente.FechaNacimiento,
                paciente.Sexo,
                paciente.Telefono,
                paciente.Direccion,
                paciente.Email
            ))
        
        conn.commit()
        return {"mensaje": f"{len(pacientes)} pacientes creados exitosamente"}
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear los pacientes: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_paciente(id: int, paciente: Paciente):
    """Actualizar un paciente existente"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Pacientes
            SET Nombre = ?, Apellido = ?, FechaNacimiento = ?, Sexo = ?, 
                Telefono = ?, Direccion = ?, Email = ?
            WHERE IdPaciente = ?
        """, (
            paciente.Nombre,
            paciente.Apellido,
            paciente.FechaNacimiento,
            paciente.Sexo,
            paciente.Telefono,
            paciente.Direccion,
            paciente.Email,
            id
        ))
        
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente con ID {id} no encontrado"
            )
        
        conn.commit()
        return {"mensaje": "Paciente actualizado exitosamente"}
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el paciente: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_paciente(id: int):
    """Eliminar un paciente"""
    conn = None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Pacientes WHERE IdPaciente = ?", (id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente con ID {id} no encontrado"
            )
        
        conn.commit()
        return {"mensaje": "Paciente eliminado exitosamente"}
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el paciente: {str(e)}"
        )
    finally:
        if conn:
            conn.close()

