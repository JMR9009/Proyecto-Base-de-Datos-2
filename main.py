from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pyodbc


app = FastAPI()


connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=MANUEL\\MSSQL2022;"
    "DATABASE=ClinicaMedica;"
    "Trusted_Connection=yes;"
)


class Medico(BaseModel):
    Nombre: str
    Apellido: str
    Especialidad: str
    Telefono: str
    Email: str

@app.post("/medicos")
def crear_medico(medico: Medico):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Medicos (Nombre, Apellido, Especialidad, Telefono, Email)
            VALUES (?, ?, ?, ?, ?)
        """, medico.Nombre, medico.Apellido, medico.Especialidad, medico.Telefono, medico.Email)
        conn.commit()
        conn.close()
        return {"mensaje": "Médico creado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/medicos")
def obtener_medicos():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Medicos")
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "IdMedico": row.IdMedico,
                "Nombre": row.Nombre,
                "Apellido": row.Apellido,
                "Especialidad": row.Especialidad,
                "Telefono": row.Telefono,
                "Email": row.Email
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/medicos/{id}")
def actualizar_medico(id: int, medico: Medico):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Medicos
            SET Nombre = ?, Apellido = ?, Especialidad = ?, Telefono = ?, Email = ?
            WHERE IdMedico = ?
        """, medico.Nombre, medico.Apellido, medico.Especialidad, medico.Telefono, medico.Email, id)
        conn.commit()
        conn.close()
        return {"mensaje": "Médico actualizado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/medicos/{id}")
def eliminar_medico(id: int):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Medicos WHERE IdMedico = ?", id)
        conn.commit()
        conn.close()
        return {"mensaje": "Médico eliminado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))