"""
Router para gestión de Departamentos
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models.departamento import Departamento, DepartamentoResponse
from database import get_db_connection
from auth import get_current_active_user
from security import safe_error_message
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/departamentos", tags=["departamentos"])


@router.get("/", response_model=List[DepartamentoResponse])
def obtener_departamentos(current_user: dict = Depends(get_current_active_user)):
    """Obtener todos los departamentos"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Departamentos ORDER BY Nombre")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener departamentos: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=DepartamentoResponse)
def obtener_departamento(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener un departamento por ID"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Departamentos WHERE IdDepartamento = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Departamento no encontrado")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener departamento: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_departamento(departamento: Departamento, current_user: dict = Depends(get_current_active_user)):
    """Crear un nuevo departamento"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Departamentos (Nombre, Descripcion, Responsable, Telefono, Email, Estado)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            departamento.Nombre,
            departamento.Descripcion,
            departamento.Responsable,
            departamento.Telefono,
            departamento.Email,
            departamento.Estado
        ))
        departamento_id = cursor.lastrowid
        conn.commit()
        return {"mensaje": "Departamento creado exitosamente", "IdDepartamento": departamento_id}
    except Exception as e:
        logger.error(f"Error al crear departamento: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_departamento(id: int, departamento: Departamento, current_user: dict = Depends(get_current_active_user)):
    """Actualizar un departamento"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdDepartamento FROM Departamentos WHERE IdDepartamento = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Departamento no encontrado")
        
        cursor.execute("""
            UPDATE Departamentos 
            SET Nombre = ?, Descripcion = ?, Responsable = ?, Telefono = ?, Email = ?, Estado = ?
            WHERE IdDepartamento = ?
        """, (
            departamento.Nombre,
            departamento.Descripcion,
            departamento.Responsable,
            departamento.Telefono,
            departamento.Email,
            departamento.Estado,
            id
        ))
        conn.commit()
        return {"mensaje": "Departamento actualizado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar departamento: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_departamento(id: int, current_user: dict = Depends(get_current_active_user)):
    """Eliminar un departamento"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdDepartamento FROM Departamentos WHERE IdDepartamento = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Departamento no encontrado")
        
        # Verificar si tiene puestos asociados
        cursor.execute("SELECT COUNT(*) FROM Puestos WHERE IdDepartamento = ?", (id,))
        if cursor.fetchone()[0] > 0:
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar el departamento porque tiene puestos asociados"
            )
        
        cursor.execute("DELETE FROM Departamentos WHERE IdDepartamento = ?", (id,))
        conn.commit()
        return {"mensaje": "Departamento eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar departamento: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

