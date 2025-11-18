"""
Router para gestión de Puestos
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models.puesto import Puesto, PuestoResponse
from database import get_db_connection
from auth import get_current_active_user
from security import safe_error_message
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/puestos", tags=["puestos"])


def validate_departamento_exists(cursor, id_departamento: int):
    """Validar que el departamento existe"""
    cursor.execute("SELECT IdDepartamento FROM Departamentos WHERE IdDepartamento = ?", (id_departamento,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Departamento no encontrado")


@router.get("/", response_model=List[PuestoResponse])
def obtener_puestos(current_user: dict = Depends(get_current_active_user)):
    """Obtener todos los puestos"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Puestos ORDER BY Nombre")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener puestos: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=PuestoResponse)
def obtener_puesto(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener un puesto por ID"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Puestos WHERE IdPuesto = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Puesto no encontrado")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener puesto: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/departamento/{id_departamento}", response_model=List[PuestoResponse])
def obtener_puestos_por_departamento(id_departamento: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener puestos por departamento"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        validate_departamento_exists(cursor, id_departamento)
        cursor.execute("SELECT * FROM Puestos WHERE IdDepartamento = ? ORDER BY Nombre", (id_departamento,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener puestos por departamento: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_puesto(puesto: Puesto, current_user: dict = Depends(get_current_active_user)):
    """Crear un nuevo puesto"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        validate_departamento_exists(cursor, puesto.IdDepartamento)
        
        cursor.execute("""
            INSERT INTO Puestos (Nombre, IdDepartamento, Nivel, Descripcion, SalarioMinimo, SalarioMaximo, Requisitos, Estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            puesto.Nombre,
            puesto.IdDepartamento,
            puesto.Nivel,
            puesto.Descripcion,
            puesto.SalarioMinimo,
            puesto.SalarioMaximo,
            puesto.Requisitos,
            puesto.Estado
        ))
        puesto_id = cursor.lastrowid
        conn.commit()
        return {"mensaje": "Puesto creado exitosamente", "IdPuesto": puesto_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear puesto: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_puesto(id: int, puesto: Puesto, current_user: dict = Depends(get_current_active_user)):
    """Actualizar un puesto"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdPuesto FROM Puestos WHERE IdPuesto = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Puesto no encontrado")
        
        validate_departamento_exists(cursor, puesto.IdDepartamento)
        
        cursor.execute("""
            UPDATE Puestos 
            SET Nombre = ?, IdDepartamento = ?, Nivel = ?, Descripcion = ?, 
                SalarioMinimo = ?, SalarioMaximo = ?, Requisitos = ?, Estado = ?
            WHERE IdPuesto = ?
        """, (
            puesto.Nombre,
            puesto.IdDepartamento,
            puesto.Nivel,
            puesto.Descripcion,
            puesto.SalarioMinimo,
            puesto.SalarioMaximo,
            puesto.Requisitos,
            puesto.Estado,
            id
        ))
        conn.commit()
        return {"mensaje": "Puesto actualizado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar puesto: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_puesto(id: int, current_user: dict = Depends(get_current_active_user)):
    """Eliminar un puesto"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdPuesto FROM Puestos WHERE IdPuesto = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Puesto no encontrado")
        
        # Verificar si tiene asignaciones asociadas
        cursor.execute("SELECT COUNT(*) FROM AsignacionesEmpleados WHERE IdPuesto = ?", (id,))
        if cursor.fetchone()[0] > 0:
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar el puesto porque tiene asignaciones asociadas"
            )
        
        cursor.execute("DELETE FROM Puestos WHERE IdPuesto = ?", (id,))
        conn.commit()
        return {"mensaje": "Puesto eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar puesto: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

