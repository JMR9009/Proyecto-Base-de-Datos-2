"""
Router para gestión de Documentación
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from models.documento import Documento, DocumentoResponse, VersionDocumento, VersionDocumentoResponse, HistorialDocumento, HistorialDocumentoResponse
from database import get_db_connection
from auth import get_current_active_user
from security import safe_error_message
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/documentos", tags=["documentos"])


@router.get("/", response_model=List[DocumentoResponse])
def obtener_documentos(current_user: dict = Depends(get_current_active_user)):
    """Obtener todos los documentos"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Documentos ORDER BY FechaCreacion DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener documentos: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=DocumentoResponse)
def obtener_documento(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener un documento por ID"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Documentos WHERE IdDocumento = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener documento: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/categoria/{categoria}", response_model=List[DocumentoResponse])
def obtener_documentos_por_categoria(categoria: str, current_user: dict = Depends(get_current_active_user)):
    """Obtener documentos por categoría"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Documentos WHERE Categoria = ? ORDER BY FechaCreacion DESC", (categoria,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener documentos por categoría: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/tipo/{tipo}", response_model=List[DocumentoResponse])
def obtener_documentos_por_tipo(tipo: str, current_user: dict = Depends(get_current_active_user)):
    """Obtener documentos por tipo"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Documentos WHERE TipoDocumento = ? ORDER BY FechaCreacion DESC", (tipo,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener documentos por tipo: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/estado/{estado}", response_model=List[DocumentoResponse])
def obtener_documentos_por_estado(estado: str, current_user: dict = Depends(get_current_active_user)):
    """Obtener documentos por estado"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Documentos WHERE Estado = ? ORDER BY FechaCreacion DESC", (estado,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener documentos por estado: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/buscar", response_model=List[DocumentoResponse])
def buscar_documentos(q: str, current_user: dict = Depends(get_current_active_user)):
    """Buscar documentos"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"%{q}%"
        cursor.execute("""
            SELECT * FROM Documentos 
            WHERE Titulo LIKE ? OR Descripcion LIKE ?
            ORDER BY FechaCreacion DESC
        """, (query, query))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al buscar documentos: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_documento(documento: Documento, current_user: dict = Depends(get_current_active_user)):
    """Crear un nuevo documento"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Convertir Tags a string si es una lista
        tags_str = ",".join(documento.Tags) if documento.Tags else None
        
        cursor.execute("""
            INSERT INTO Documentos (Titulo, Descripcion, Categoria, TipoDocumento, Version, ArchivoUrl, ArchivoNombre,
                                   TamañoArchivo, Estado, Visibilidad, Tags, IdCreador, IdDepartamento,
                                   FechaPublicacion, FechaVencimiento, Observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            documento.Titulo,
            documento.Descripcion,
            documento.Categoria,
            documento.TipoDocumento,
            documento.Version,
            documento.ArchivoUrl,
            documento.ArchivoNombre,
            documento.TamañoArchivo,
            documento.Estado,
            documento.Visibilidad,
            tags_str,
            documento.IdCreador or current_user.get("IdUsuario"),
            documento.IdDepartamento,
            documento.FechaPublicacion,
            documento.FechaVencimiento,
            documento.Observaciones
        ))
        documento_id = cursor.lastrowid
        
        # Registrar en historial
        cursor.execute("""
            INSERT INTO HistorialDocumento (IdDocumento, Accion, IdUsuario, Comentarios)
            VALUES (?, 'creado', ?, ?)
        """, (documento_id, current_user.get("IdUsuario"), "Documento creado"))
        
        conn.commit()
        return {"mensaje": "Documento creado exitosamente", "IdDocumento": documento_id}
    except Exception as e:
        logger.error(f"Error al crear documento: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_documento(id: int, documento: Documento, current_user: dict = Depends(get_current_active_user)):
    """Actualizar un documento"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdDocumento FROM Documentos WHERE IdDocumento = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        tags_str = ",".join(documento.Tags) if documento.Tags else None
        
        cursor.execute("""
            UPDATE Documentos 
            SET Titulo = ?, Descripcion = ?, Categoria = ?, TipoDocumento = ?, Version = ?, ArchivoUrl = ?,
                ArchivoNombre = ?, TamañoArchivo = ?, Estado = ?, Visibilidad = ?, Tags = ?, IdDepartamento = ?,
                FechaPublicacion = ?, FechaVencimiento = ?, Observaciones = ?, FechaActualizacion = ?
            WHERE IdDocumento = ?
        """, (
            documento.Titulo,
            documento.Descripcion,
            documento.Categoria,
            documento.TipoDocumento,
            documento.Version,
            documento.ArchivoUrl,
            documento.ArchivoNombre,
            documento.TamañoArchivo,
            documento.Estado,
            documento.Visibilidad,
            tags_str,
            documento.IdDepartamento,
            documento.FechaPublicacion,
            documento.FechaVencimiento,
            documento.Observaciones,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            id
        ))
        
        # Registrar en historial
        cursor.execute("""
            INSERT INTO HistorialDocumento (IdDocumento, Accion, IdUsuario, Comentarios)
            VALUES (?, 'actualizado', ?, ?)
        """, (id, current_user.get("IdUsuario"), "Documento actualizado"))
        
        conn.commit()
        return {"mensaje": "Documento actualizado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar documento: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/{id}/publicar", response_model=dict)
def publicar_documento(id: int, current_user: dict = Depends(get_current_active_user)):
    """Publicar un documento"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdDocumento FROM Documentos WHERE IdDocumento = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        cursor.execute("""
            UPDATE Documentos 
            SET Estado = 'publicado', FechaPublicacion = ?, FechaActualizacion = ?
            WHERE IdDocumento = ?
        """, (datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id))
        
        # Registrar en historial
        cursor.execute("""
            INSERT INTO HistorialDocumento (IdDocumento, Accion, IdUsuario)
            VALUES (?, 'publicado', ?)
        """, (id, current_user.get("IdUsuario")))
        
        conn.commit()
        return {"mensaje": "Documento publicado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al publicar documento: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/{id}/archivar", response_model=dict)
def archivar_documento(id: int, current_user: dict = Depends(get_current_active_user)):
    """Archivar un documento"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdDocumento FROM Documentos WHERE IdDocumento = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        cursor.execute("""
            UPDATE Documentos 
            SET Estado = 'archivado', FechaActualizacion = ?
            WHERE IdDocumento = ?
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id))
        
        # Registrar en historial
        cursor.execute("""
            INSERT INTO HistorialDocumento (IdDocumento, Accion, IdUsuario)
            VALUES (?, 'archivado', ?)
        """, (id, current_user.get("IdUsuario")))
        
        conn.commit()
        return {"mensaje": "Documento archivado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al archivar documento: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_documento(id: int, current_user: dict = Depends(get_current_active_user)):
    """Eliminar un documento"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdDocumento FROM Documentos WHERE IdDocumento = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        # Eliminar versiones asociadas
        cursor.execute("DELETE FROM VersionesDocumento WHERE IdDocumento = ?", (id,))
        
        # Eliminar historial asociado
        cursor.execute("DELETE FROM HistorialDocumento WHERE IdDocumento = ?", (id,))
        
        cursor.execute("DELETE FROM Documentos WHERE IdDocumento = ?", (id,))
        conn.commit()
        return {"mensaje": "Documento eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar documento: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}/versiones", response_model=List[VersionDocumentoResponse])
def obtener_versiones_documento(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener versiones de un documento"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM VersionesDocumento WHERE IdDocumento = ? ORDER BY FechaCreacion DESC", (id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener versiones: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}/historial", response_model=List[HistorialDocumentoResponse])
def obtener_historial_documento(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener historial de un documento"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM HistorialDocumento WHERE IdDocumento = ? ORDER BY FechaAccion DESC", (id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener historial: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

