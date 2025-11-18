"""
Router para gestión de Conceptos de Nómina
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models.nomina import ConceptoNomina, ConceptoNominaResponse
from database import get_db_connection
from auth import get_current_active_user
from security import safe_error_message
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/conceptos-nomina", tags=["conceptos-nomina"])


@router.get("/", response_model=List[ConceptoNominaResponse])
def obtener_conceptos(current_user: dict = Depends(get_current_active_user)):
    """Obtener todos los conceptos de nómina"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ConceptosNomina ORDER BY Orden, Nombre")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener conceptos: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=ConceptoNominaResponse)
def obtener_concepto(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener un concepto por ID"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ConceptosNomina WHERE IdConcepto = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Concepto no encontrado")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener concepto: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/activos", response_model=List[ConceptoNominaResponse])
def obtener_conceptos_activos(current_user: dict = Depends(get_current_active_user)):
    """Obtener conceptos activos"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ConceptosNomina WHERE Activo = 1 ORDER BY Orden, Nombre")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener conceptos activos: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/tipo/{tipo}", response_model=List[ConceptoNominaResponse])
def obtener_conceptos_por_tipo(tipo: str, current_user: dict = Depends(get_current_active_user)):
    """Obtener conceptos por tipo"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ConceptosNomina WHERE Tipo = ? ORDER BY Orden, Nombre", (tipo,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener conceptos por tipo: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_concepto(concepto: ConceptoNomina, current_user: dict = Depends(get_current_active_user)):
    """Crear un nuevo concepto de nómina"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validar referencias si aplica
        if concepto.AplicaA == "departamento" and concepto.IdDepartamento:
            cursor.execute("SELECT IdDepartamento FROM Departamentos WHERE IdDepartamento = ?", (concepto.IdDepartamento,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Departamento no encontrado")
        
        if concepto.AplicaA == "puesto" and concepto.IdPuesto:
            cursor.execute("SELECT IdPuesto FROM Puestos WHERE IdPuesto = ?", (concepto.IdPuesto,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Puesto no encontrado")
        
        if concepto.AplicaA == "empleado" and concepto.IdEmpleado:
            cursor.execute("SELECT IdEmpleado FROM Empleados WHERE IdEmpleado = ?", (concepto.IdEmpleado,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Empleado no encontrado")
        
        cursor.execute("""
            INSERT INTO ConceptosNomina (Nombre, Descripcion, Tipo, TipoCalculo, Valor, AplicaA,
                                        IdDepartamento, IdPuesto, IdEmpleado, Activo, Orden)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            concepto.Nombre,
            concepto.Descripcion,
            concepto.Tipo,
            concepto.TipoCalculo,
            concepto.Valor,
            concepto.AplicaA,
            concepto.IdDepartamento,
            concepto.IdPuesto,
            concepto.IdEmpleado,
            1 if concepto.Activo else 0,
            concepto.Orden
        ))
        concepto_id = cursor.lastrowid
        conn.commit()
        return {"mensaje": "Concepto creado exitosamente", "IdConcepto": concepto_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear concepto: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_concepto(id: int, concepto: ConceptoNomina, current_user: dict = Depends(get_current_active_user)):
    """Actualizar un concepto"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdConcepto FROM ConceptosNomina WHERE IdConcepto = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Concepto no encontrado")
        
        # Validar referencias si aplica
        if concepto.AplicaA == "departamento" and concepto.IdDepartamento:
            cursor.execute("SELECT IdDepartamento FROM Departamentos WHERE IdDepartamento = ?", (concepto.IdDepartamento,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Departamento no encontrado")
        
        if concepto.AplicaA == "puesto" and concepto.IdPuesto:
            cursor.execute("SELECT IdPuesto FROM Puestos WHERE IdPuesto = ?", (concepto.IdPuesto,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Puesto no encontrado")
        
        if concepto.AplicaA == "empleado" and concepto.IdEmpleado:
            cursor.execute("SELECT IdEmpleado FROM Empleados WHERE IdEmpleado = ?", (concepto.IdEmpleado,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Empleado no encontrado")
        
        cursor.execute("""
            UPDATE ConceptosNomina 
            SET Nombre = ?, Descripcion = ?, Tipo = ?, TipoCalculo = ?, Valor = ?, AplicaA = ?,
                IdDepartamento = ?, IdPuesto = ?, IdEmpleado = ?, Activo = ?, Orden = ?
            WHERE IdConcepto = ?
        """, (
            concepto.Nombre,
            concepto.Descripcion,
            concepto.Tipo,
            concepto.TipoCalculo,
            concepto.Valor,
            concepto.AplicaA,
            concepto.IdDepartamento,
            concepto.IdPuesto,
            concepto.IdEmpleado,
            1 if concepto.Activo else 0,
            concepto.Orden,
            id
        ))
        conn.commit()
        return {"mensaje": "Concepto actualizado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar concepto: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_concepto(id: int, current_user: dict = Depends(get_current_active_user)):
    """Eliminar un concepto"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdConcepto FROM ConceptosNomina WHERE IdConcepto = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Concepto no encontrado")
        
        cursor.execute("DELETE FROM ConceptosNomina WHERE IdConcepto = ?", (id,))
        conn.commit()
        return {"mensaje": "Concepto eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar concepto: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

