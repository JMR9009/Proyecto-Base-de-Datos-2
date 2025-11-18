"""
Router para gestión de Categorías de Documentos
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models.documento import CategoriaDocumento, CategoriaDocumentoResponse
from database import get_db_connection
from auth import get_current_active_user
from security import safe_error_message
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/categorias-documento", tags=["categorias-documento"])


@router.get("/", response_model=List[CategoriaDocumentoResponse])
def obtener_categorias(current_user: dict = Depends(get_current_active_user)):
    """Obtener todas las categorías"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM CategoriasDocumento ORDER BY Orden, Nombre")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener categorías: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=CategoriaDocumentoResponse)
def obtener_categoria(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener una categoría por ID"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM CategoriasDocumento WHERE IdCategoria = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener categoría: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_categoria(categoria: CategoriaDocumento, current_user: dict = Depends(get_current_active_user)):
    """Crear una nueva categoría"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO CategoriasDocumento (Nombre, Descripcion, Icono, Color, Orden, Activa)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            categoria.Nombre,
            categoria.Descripcion,
            categoria.Icono,
            categoria.Color,
            categoria.Orden,
            1 if categoria.Activa else 0
        ))
        categoria_id = cursor.lastrowid
        conn.commit()
        return {"mensaje": "Categoría creada exitosamente", "IdCategoria": categoria_id}
    except Exception as e:
        logger.error(f"Error al crear categoría: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_categoria(id: int, categoria: CategoriaDocumento, current_user: dict = Depends(get_current_active_user)):
    """Actualizar una categoría"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdCategoria FROM CategoriasDocumento WHERE IdCategoria = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        
        cursor.execute("""
            UPDATE CategoriasDocumento 
            SET Nombre = ?, Descripcion = ?, Icono = ?, Color = ?, Orden = ?, Activa = ?
            WHERE IdCategoria = ?
        """, (
            categoria.Nombre,
            categoria.Descripcion,
            categoria.Icono,
            categoria.Color,
            categoria.Orden,
            1 if categoria.Activa else 0,
            id
        ))
        conn.commit()
        return {"mensaje": "Categoría actualizada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar categoría: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_categoria(id: int, current_user: dict = Depends(get_current_active_user)):
    """Eliminar una categoría"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdCategoria FROM CategoriasDocumento WHERE IdCategoria = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        
        # Verificar si tiene documentos asociados
        cursor.execute("SELECT COUNT(*) FROM Documentos WHERE Categoria = (SELECT Nombre FROM CategoriasDocumento WHERE IdCategoria = ?)", (id,))
        if cursor.fetchone()[0] > 0:
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar la categoría porque tiene documentos asociados"
            )
        
        cursor.execute("DELETE FROM CategoriasDocumento WHERE IdCategoria = ?", (id,))
        conn.commit()
        return {"mensaje": "Categoría eliminada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar categoría: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

