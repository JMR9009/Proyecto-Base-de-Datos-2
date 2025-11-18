"""
Router para gestión de Roles
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models.usuario_rol import Rol, RolResponse
from database import get_db_connection
from auth import get_current_active_user
from security import safe_error_message
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=List[RolResponse])
def obtener_roles(current_user: dict = Depends(get_current_active_user)):
    """Obtener todos los roles"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Roles ORDER BY Nombre")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener roles: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=RolResponse)
def obtener_rol(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener un rol por ID"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Roles WHERE IdRol = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Rol no encontrado")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener rol: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_rol(rol: Rol, current_user: dict = Depends(get_current_active_user)):
    """Crear un nuevo rol"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que el nombre no existe
        cursor.execute("SELECT IdRol FROM Roles WHERE Nombre = ?", (rol.Nombre,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El nombre del rol ya existe")
        
        permisos_str = ",".join(rol.Permisos) if rol.Permisos else None
        
        cursor.execute("""
            INSERT INTO Roles (Nombre, Descripcion, Activo)
            VALUES (?, ?, ?)
        """, (
            rol.Nombre,
            rol.Descripcion,
            1 if rol.Activo else 0
        ))
        rol_id = cursor.lastrowid
        
        # Asignar permisos si se proporcionan
        if rol.Permisos:
            for permiso_nombre in rol.Permisos:
                cursor.execute("""
                    INSERT INTO RolesPermisos (IdRol, IdPermiso)
                    SELECT ?, IdPermiso FROM Permisos WHERE Nombre = ?
                """, (rol_id, permiso_nombre))
        
        conn.commit()
        return {"mensaje": "Rol creado exitosamente", "IdRol": rol_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear rol: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_rol(id: int, rol: Rol, current_user: dict = Depends(get_current_active_user)):
    """Actualizar un rol"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdRol FROM Roles WHERE IdRol = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Rol no encontrado")
        
        # Verificar que el nombre no existe en otro rol
        cursor.execute("SELECT IdRol FROM Roles WHERE Nombre = ? AND IdRol != ?", (rol.Nombre, id))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El nombre del rol ya existe")
        
        cursor.execute("""
            UPDATE Roles 
            SET Nombre = ?, Descripcion = ?, Activo = ?
            WHERE IdRol = ?
        """, (
            rol.Nombre,
            rol.Descripcion,
            1 if rol.Activo else 0,
            id
        ))
        
        # Actualizar permisos si se proporcionan
        if rol.Permisos is not None:
            # Eliminar permisos actuales
            cursor.execute("DELETE FROM RolesPermisos WHERE IdRol = ?", (id,))
            # Asignar nuevos permisos
            for permiso_nombre in rol.Permisos:
                cursor.execute("""
                    INSERT INTO RolesPermisos (IdRol, IdPermiso)
                    SELECT ?, IdPermiso FROM Permisos WHERE Nombre = ?
                """, (id, permiso_nombre))
        
        conn.commit()
        return {"mensaje": "Rol actualizado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar rol: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/{id}/permisos", response_model=dict)
def asignar_permisos(id: int, data: dict, current_user: dict = Depends(get_current_active_user)):
    """Asignar permisos a un rol"""
    conn = None
    try:
        permisos = data.get("permisos")
        if not permisos or not isinstance(permisos, list):
            raise HTTPException(status_code=400, detail="permisos debe ser una lista")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdRol FROM Roles WHERE IdRol = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Rol no encontrado")
        
        # Eliminar permisos actuales
        cursor.execute("DELETE FROM RolesPermisos WHERE IdRol = ?", (id,))
        
        # Asignar nuevos permisos
        for permiso_nombre in permisos:
            cursor.execute("""
                INSERT INTO RolesPermisos (IdRol, IdPermiso)
                SELECT ?, IdPermiso FROM Permisos WHERE Nombre = ?
            """, (id, permiso_nombre))
        
        conn.commit()
        return {"mensaje": "Permisos asignados exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al asignar permisos: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_rol(id: int, current_user: dict = Depends(get_current_active_user)):
    """Eliminar un rol"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdRol FROM Roles WHERE IdRol = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Rol no encontrado")
        
        # Verificar si tiene usuarios asociados
        cursor.execute("SELECT COUNT(*) FROM Usuarios WHERE Rol = (SELECT Nombre FROM Roles WHERE IdRol = ?)", (id,))
        if cursor.fetchone()[0] > 0:
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar el rol porque tiene usuarios asociados"
            )
        
        # Eliminar permisos asociados
        cursor.execute("DELETE FROM RolesPermisos WHERE IdRol = ?", (id,))
        
        cursor.execute("DELETE FROM Roles WHERE IdRol = ?", (id,))
        conn.commit()
        return {"mensaje": "Rol eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar rol: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/permisos/list", response_model=List)
def obtener_permisos_disponibles(current_user: dict = Depends(get_current_active_user)):
    """Obtener todos los permisos disponibles"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Permisos ORDER BY Modulo, Nombre")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener permisos: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

