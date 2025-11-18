"""
Router para gestión de Usuarios (CRUD extendido)
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models.usuario_rol import Usuario, UsuarioResponse
from database import get_db_connection
from auth import get_current_active_user, get_password_hash
from security import safe_error_message
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("/", response_model=List[UsuarioResponse])
def obtener_usuarios(current_user: dict = Depends(get_current_active_user)):
    """Obtener todos los usuarios"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Usuarios ORDER BY NombreUsuario")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener usuarios: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}", response_model=UsuarioResponse)
def obtener_usuario(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener un usuario por ID"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Usuarios WHERE IdUsuario = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener usuario: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/rol/{id_rol}", response_model=List[UsuarioResponse])
def obtener_usuarios_por_rol(id_rol: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener usuarios por rol"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Usuarios WHERE Rol = (SELECT Nombre FROM Roles WHERE IdRol = ?) ORDER BY NombreUsuario", (id_rol,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener usuarios por rol: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/estado/{estado}", response_model=List[UsuarioResponse])
def obtener_usuarios_por_estado(estado: str, current_user: dict = Depends(get_current_active_user)):
    """Obtener usuarios por estado"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Mapear estado a Activo
        activo = 1 if estado == "activo" else 0
        cursor.execute("SELECT * FROM Usuarios WHERE Activo = ? ORDER BY NombreUsuario", (activo,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener usuarios por estado: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: Usuario, current_user: dict = Depends(get_current_active_user)):
    """Crear un nuevo usuario"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que el username no existe
        cursor.execute("SELECT IdUsuario FROM Usuarios WHERE Username = ?", (usuario.NombreUsuario,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
        
        # Verificar que el email no existe
        cursor.execute("SELECT IdUsuario FROM Usuarios WHERE Email = ?", (usuario.Email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El email ya existe")
        
        # Hash de password si se proporciona
        password_hash = None
        if usuario.Password:
            password_hash = get_password_hash(usuario.Password)
        else:
            raise HTTPException(status_code=400, detail="La contraseña es requerida")
        
        # Obtener nombre del rol si se proporciona IdRol
        rol_nombre = None
        if usuario.IdRol:
            cursor.execute("SELECT Nombre FROM Roles WHERE IdRol = ?", (usuario.IdRol,))
            rol_row = cursor.fetchone()
            if not rol_row:
                raise HTTPException(status_code=404, detail="Rol no encontrado")
            rol_nombre = rol_row[0]
        
        cursor.execute("""
            INSERT INTO Usuarios (Username, PasswordHash, Email, Rol, Activo)
            VALUES (?, ?, ?, ?, ?)
        """, (
            usuario.NombreUsuario,
            password_hash,
            usuario.Email,
            rol_nombre or "usuario",
            1 if usuario.Estado == "activo" else 0
        ))
        usuario_id = cursor.lastrowid
        conn.commit()
        return {"mensaje": "Usuario creado exitosamente", "IdUsuario": usuario_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear usuario: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.put("/{id}", response_model=dict)
def actualizar_usuario(id: int, usuario: Usuario, current_user: dict = Depends(get_current_active_user)):
    """Actualizar un usuario"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdUsuario FROM Usuarios WHERE IdUsuario = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Verificar que el username no existe en otro usuario
        cursor.execute("SELECT IdUsuario FROM Usuarios WHERE Username = ? AND IdUsuario != ?", (usuario.NombreUsuario, id))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
        
        # Verificar que el email no existe en otro usuario
        cursor.execute("SELECT IdUsuario FROM Usuarios WHERE Email = ? AND IdUsuario != ?", (usuario.Email, id))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El email ya existe")
        
        # Hash de password si se proporciona
        password_hash = None
        if usuario.Password:
            password_hash = get_password_hash(usuario.Password)
        
        # Obtener nombre del rol si se proporciona IdRol
        rol_nombre = None
        if usuario.IdRol:
            cursor.execute("SELECT Nombre FROM Roles WHERE IdRol = ?", (usuario.IdRol,))
            rol_row = cursor.fetchone()
            if not rol_row:
                raise HTTPException(status_code=404, detail="Rol no encontrado")
            rol_nombre = rol_row[0]
        
        if password_hash:
            cursor.execute("""
                UPDATE Usuarios 
                SET Username = ?, PasswordHash = ?, Email = ?, Rol = ?, Activo = ?
                WHERE IdUsuario = ?
            """, (
                usuario.NombreUsuario,
                password_hash,
                usuario.Email,
                rol_nombre,
                1 if usuario.Estado == "activo" else 0,
                id
            ))
        else:
            cursor.execute("""
                UPDATE Usuarios 
                SET Username = ?, Email = ?, Rol = ?, Activo = ?
                WHERE IdUsuario = ?
            """, (
                usuario.NombreUsuario,
                usuario.Email,
                rol_nombre,
                1 if usuario.Estado == "activo" else 0,
                id
            ))
        
        conn.commit()
        return {"mensaje": "Usuario actualizado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar usuario: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/{id}/cambiar-password", response_model=dict)
def cambiar_password(id: int, data: dict, current_user: dict = Depends(get_current_active_user)):
    """Cambiar contraseña de un usuario"""
    conn = None
    try:
        from auth import verify_password
        password_actual = data.get("passwordActual")
        password_nueva = data.get("passwordNueva")
        
        if not password_actual or not password_nueva:
            raise HTTPException(status_code=400, detail="passwordActual y passwordNueva son requeridos")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT PasswordHash FROM Usuarios WHERE IdUsuario = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        if not verify_password(password_actual, row[0]):
            raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
        
        nuevo_hash = get_password_hash(password_nueva)
        cursor.execute("UPDATE Usuarios SET PasswordHash = ? WHERE IdUsuario = ?", (nuevo_hash, id))
        conn.commit()
        return {"mensaje": "Contraseña cambiada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cambiar contraseña: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/{id}/reset-password", response_model=dict)
def reset_password(id: int, current_user: dict = Depends(get_current_active_user)):
    """Resetear contraseña de un usuario"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdUsuario FROM Usuarios WHERE IdUsuario = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Resetear a password por defecto
        password_default = "password123"
        nuevo_hash = get_password_hash(password_default)
        cursor.execute("UPDATE Usuarios SET PasswordHash = ? WHERE IdUsuario = ?", (nuevo_hash, id))
        conn.commit()
        return {"mensaje": "Contraseña reseteada exitosamente", "password": password_default}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al resetear contraseña: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/{id}/activar", response_model=dict)
def activar_usuario(id: int, current_user: dict = Depends(get_current_active_user)):
    """Activar un usuario"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdUsuario FROM Usuarios WHERE IdUsuario = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        cursor.execute("UPDATE Usuarios SET Activo = 1 WHERE IdUsuario = ?", (id,))
        conn.commit()
        return {"mensaje": "Usuario activado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al activar usuario: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/{id}/desactivar", response_model=dict)
def desactivar_usuario(id: int, current_user: dict = Depends(get_current_active_user)):
    """Desactivar un usuario"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdUsuario FROM Usuarios WHERE IdUsuario = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        cursor.execute("UPDATE Usuarios SET Activo = 0 WHERE IdUsuario = ?", (id,))
        conn.commit()
        return {"mensaje": "Usuario desactivado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al desactivar usuario: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/{id}/bloquear", response_model=dict)
def bloquear_usuario(id: int, current_user: dict = Depends(get_current_active_user)):
    """Bloquear un usuario"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdUsuario FROM Usuarios WHERE IdUsuario = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        cursor.execute("UPDATE Usuarios SET Activo = 0 WHERE IdUsuario = ?", (id,))
        conn.commit()
        return {"mensaje": "Usuario bloqueado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al bloquear usuario: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/{id}/desbloquear", response_model=dict)
def desbloquear_usuario(id: int, current_user: dict = Depends(get_current_active_user)):
    """Desbloquear un usuario"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdUsuario FROM Usuarios WHERE IdUsuario = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        cursor.execute("UPDATE Usuarios SET Activo = 1 WHERE IdUsuario = ?", (id,))
        conn.commit()
        return {"mensaje": "Usuario desbloqueado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al desbloquear usuario: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.post("/{id}/asignar-rol", response_model=dict)
def asignar_rol(id: int, data: dict, current_user: dict = Depends(get_current_active_user)):
    """Asignar un rol a un usuario"""
    conn = None
    try:
        id_rol = data.get("idRol")
        if not id_rol:
            raise HTTPException(status_code=400, detail="idRol es requerido")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdUsuario FROM Usuarios WHERE IdUsuario = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        cursor.execute("SELECT Nombre FROM Roles WHERE IdRol = ?", (id_rol,))
        rol_row = cursor.fetchone()
        if not rol_row:
            raise HTTPException(status_code=404, detail="Rol no encontrado")
        
        cursor.execute("UPDATE Usuarios SET Rol = ? WHERE IdUsuario = ?", (rol_row[0], id))
        conn.commit()
        return {"mensaje": "Rol asignado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al asignar rol: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.delete("/{id}", response_model=dict)
def eliminar_usuario(id: int, current_user: dict = Depends(get_current_active_user)):
    """Eliminar un usuario"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT IdUsuario FROM Usuarios WHERE IdUsuario = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        cursor.execute("DELETE FROM Usuarios WHERE IdUsuario = ?", (id,))
        conn.commit()
        return {"mensaje": "Usuario eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar usuario: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()


@router.get("/{id}/historial", response_model=List)
def obtener_historial_usuario(id: int, current_user: dict = Depends(get_current_active_user)):
    """Obtener historial de un usuario"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM HistorialUsuario WHERE IdUsuario = ? ORDER BY FechaAccion DESC", (id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener historial: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

