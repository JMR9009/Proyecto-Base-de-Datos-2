"""
Módulo de autenticación JWT
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import get_db_connection
import os
import logging

logger = logging.getLogger(__name__)

# Configuración de seguridad
SECRET_KEY = os.getenv("SECRET_KEY", "tu-clave-secreta-super-segura-cambiar-en-produccion")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
# Duración del token: 1 mes = 30 días = 43,200 minutos
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))

# Contexto para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema de seguridad HTTP Bearer
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña contra hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generar hash de contraseña"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crear token JWT"""
    to_encode = data.copy()
    
    # Asegurar que 'sub' sea string (requerido por JWT)
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verificar y decodificar token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"Error al verificar token: {str(e)}")
        return None


def get_user_by_username(username: str):
    """Obtener usuario por username desde la BD"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT IdUsuario, Username, PasswordHash, Email, Rol, Activo FROM Usuarios WHERE Username = ? AND Activo = 1",
            (username,)
        )
        row = cursor.fetchone()
        if row:
            return {
                "IdUsuario": row[0],
                "Username": row[1],
                "PasswordHash": row[2],
                "Email": row[3],
                "Rol": row[4],
                "Activo": row[5]
            }
        return None
    except Exception as e:
        logger.error(f"Error al obtener usuario: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()


def get_user_by_id(user_id: int):
    """Obtener usuario por ID desde la BD"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT IdUsuario, Username, Email, Rol, Activo FROM Usuarios WHERE IdUsuario = ? AND Activo = 1",
            (user_id,)
        )
        row = cursor.fetchone()
        if row:
            return {
                "IdUsuario": row[0],
                "Username": row[1],
                "Email": row[2],
                "Rol": row[3],
                "Activo": row[4]
            }
        return None
    except Exception as e:
        logger.error(f"Error al obtener usuario por ID: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Obtener usuario actual desde el token JWT"""
    token = credentials.credentials
    
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Convertir string a int
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Obtener usuario activo actual"""
    if not current_user.get("Activo"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    return current_user


def require_role(required_role: str):
    """Dependency para requerir un rol específico"""
    async def role_checker(current_user: dict = Depends(get_current_active_user)):
        user_role = current_user.get("Rol", "").lower()
        if user_role != required_role.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere rol: {required_role}"
            )
        return current_user
    return role_checker

