"""
Router para gestión de Versiones de Documentos
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models.documento import VersionDocumento, VersionDocumentoResponse
from database import get_db_connection
from auth import get_current_active_user
from security import safe_error_message
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/versiones-documento", tags=["versiones-documento"])


@router.get("/{id}", response_model=VersionDocumentoResponse)
def obtener_version(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener una versión por ID"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM VersionesDocumento WHERE IdVersion = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Versión no encontrada")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener versión: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_version(version: VersionDocumento, current_user: dict = Depends(get_current_active_user)):
    """Crear una nueva versión de documento"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que el documento existe
        cursor.execute("SELECT IdDocumento FROM Documentos WHERE IdDocumento = ?", (version.IdDocumento,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        # Marcar todas las versiones anteriores como no actuales
        cursor.execute("""
            UPDATE VersionesDocumento 
            SET EsVersionActual = 0 
            WHERE IdDocumento = ?
        """, (version.IdDocumento,))
        
        cursor.execute("""
            INSERT INTO VersionesDocumento (IdDocumento, Version, Cambios, ArchivoUrl, ArchivoNombre,
                                           TamañoArchivo, IdCreador, EsVersionActual)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            version.IdDocumento,
            version.Version,
            version.Cambios,
            version.ArchivoUrl,
            version.ArchivoNombre,
            version.TamañoArchivo,
            version.IdCreador or current_user.get("IdUsuario"),
            1 if version.EsVersionActual else 0
        ))
        version_id = cursor.lastrowid
        
        # Actualizar la versión del documento principal si es la versión actual
        if version.EsVersionActual:
            cursor.execute("""
                UPDATE Documentos 
                SET Version = ?, ArchivoUrl = ?, ArchivoNombre = ?, TamañoArchivo = ?
                WHERE IdDocumento = ?
            """, (
                version.Version,
                version.ArchivoUrl,
                version.ArchivoNombre,
                version.TamañoArchivo,
                version.IdDocumento
            ))
        
        conn.commit()
        return {"mensaje": "Versión creada exitosamente", "IdVersion": version_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear versión: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/{id}/restaurar", response_model=dict)
def restaurar_version(id: int, current_user: dict = Depends(get_current_active_user)):
    """Restaurar una versión como la versión actual"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM VersionesDocumento WHERE IdVersion = ?", (id,))
        version = cursor.fetchone()
        if not version:
            raise HTTPException(status_code=404, detail="Versión no encontrada")
        
        version_dict = dict(version)
        
        # Marcar todas las versiones como no actuales
        cursor.execute("""
            UPDATE VersionesDocumento 
            SET EsVersionActual = 0 
            WHERE IdDocumento = ?
        """, (version_dict["IdDocumento"],))
        
        # Marcar esta versión como actual
        cursor.execute("""
            UPDATE VersionesDocumento 
            SET EsVersionActual = 1 
            WHERE IdVersion = ?
        """, (id,))
        
        # Actualizar el documento principal
        cursor.execute("""
            UPDATE Documentos 
            SET Version = ?, ArchivoUrl = ?, ArchivoNombre = ?, TamañoArchivo = ?
            WHERE IdDocumento = ?
        """, (
            version_dict["Version"],
            version_dict["ArchivoUrl"],
            version_dict["ArchivoNombre"],
            version_dict["TamañoArchivo"],
            version_dict["IdDocumento"]
        ))
        
        conn.commit()
        return {"mensaje": "Versión restaurada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al restaurar versión: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

