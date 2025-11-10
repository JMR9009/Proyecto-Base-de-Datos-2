from fastapi import APIRouter, HTTPException
from models.cita import Cita
from pydantic import BaseModel
from datetime import datetime
from typing import List
import pyodbc

router = APIRouter(prefix="/citas", tags=["citas"])

connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=MANUEL\\MSSQL2022;"
    "DATABASE=ClinicaMedica;"
    "Trusted_Connection=yes;"
)


class CitaResponse(BaseModel):
    IdCita: int
    IdPaciente: int
    IdMedico: int
    FechaCita: datetime
    Motivo: str
    Estado: str


@router.post("/", response_model=dict)
def crear_cita(cita: Cita):
    """Crear una nueva cita"""
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Citas (IdPaciente, IdMedico, FechaCita, Motivo, Estado)
            VALUES (?, ?, ?, ?, ?)
        """, cita.IdPaciente, cita.IdMedico, cita.FechaCita, cita.Motivo, cita.Estado)
        conn.commit()
        conn.close()
        return {"mensaje": "Cita creada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[CitaResponse])
def obtener_citas():
    """Obtener todas las citas"""
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Citas")
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "IdCita": row.IdCita,
                "IdPaciente": row.IdPaciente,
                "IdMedico": row.IdMedico,
                "FechaCita": row.FechaCita,
                "Motivo": row.Motivo,
                "Estado": row.Estado
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}", response_model=CitaResponse)
def obtener_cita(id: int):
    """Obtener una cita por ID"""
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Citas WHERE IdCita = ?", id)
        row = cursor.fetchone()
        conn.close()
        if row is None:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        return {
            "IdCita": row.IdCita,
            "IdPaciente": row.IdPaciente,
            "IdMedico": row.IdMedico,
            "FechaCita": row.FechaCita,
            "Motivo": row.Motivo,
            "Estado": row.Estado
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{id}", response_model=dict)
def actualizar_cita(id: int, cita: Cita):
    """Actualizar una cita existente"""
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Citas
            SET IdPaciente = ?, IdMedico = ?, FechaCita = ?, Motivo = ?, Estado = ?
            WHERE IdCita = ?
        """, cita.IdPaciente, cita.IdMedico, cita.FechaCita, cita.Motivo, cita.Estado, id)
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        conn.commit()
        conn.close()
        return {"mensaje": "Cita actualizada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{id}", response_model=dict)
def eliminar_cita(id: int):
    """Eliminar una cita"""
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Citas WHERE IdCita = ?", id)
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        conn.commit()
        conn.close()
        return {"mensaje": "Cita eliminada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

