"""
Router para gestión de Historial de Documentos
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.documento import HistorialDocumentoResponse
from database import get_db_connection
from auth import get_current_active_user
from security import safe_error_message
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/historial-documentos", tags=["historial-documentos"])


@router.get("/", response_model=List[HistorialDocumentoResponse])
def obtener_historial_completo(current_user: dict = Depends(get_current_active_user)):
    """Obtener todo el historial de documentos"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM HistorialDocumento ORDER BY FechaAccion DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener historial: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

