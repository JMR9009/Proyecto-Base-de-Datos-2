"""
Router de autenticación JWT
"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_user_by_username,
    get_current_active_user
)
from database import get_db_connection
from security import sanitize_string, safe_error_message
import os
import logging

logger = logging.getLogger(__name__)
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

router = APIRouter(prefix="/auth", tags=["autenticación"])


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    
    @validator('username')
    def sanitize_username(cls, v):
        return sanitize_string(v, max_length=50).lower()


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    email: EmailStr
    rol: Optional[str] = Field(default="usuario", max_length=20)
    
    @validator('username')
    def sanitize_username(cls, v):
        return sanitize_string(v, max_length=50).lower()
    
    @validator('rol')
    def sanitize_rol(cls, v):
        if v:
            return sanitize_string(v, max_length=20).lower()
        return "usuario"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    IdUsuario: int
    Username: str
    Email: str
    Rol: str


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest):
    """Endpoint de login - Obtener token JWT"""
    conn = None
    try:
        # Verificar usuario
        user = get_user_by_username(login_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos"
            )
        
        # Verificar contraseña
        if not verify_password(login_data.password, user["PasswordHash"]):
            logger.warning(f"Intento de login fallido para usuario: {login_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos"
            )
        
        # Crear token
        access_token = create_access_token(data={"sub": user["IdUsuario"]})
        
        logger.info(f"Login exitoso para usuario: {login_data.username}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "IdUsuario": user["IdUsuario"],
                "Username": user["Username"],
                "Email": user["Email"],
                "Rol": user["Rol"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
    finally:
        if conn:
            conn.close()


@router.post("/register", response_model=TokenResponse)
def register(register_data: RegisterRequest):
    """Endpoint de registro - Crear nuevo usuario"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si el usuario ya existe
        cursor.execute("SELECT COUNT(*) FROM Usuarios WHERE Username = ? OR Email = ?", 
                      (register_data.username, register_data.email))
        if cursor.fetchone()[0] > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario o email ya existe"
            )
        
        # Crear hash de contraseña
        password_hash = get_password_hash(register_data.password)
        
        # Insertar usuario
        cursor.execute("""
            INSERT INTO Usuarios (Username, PasswordHash, Email, Rol, Activo)
            VALUES (?, ?, ?, ?, ?)
        """, (
            register_data.username,
            password_hash,
            register_data.email,
            register_data.rol,
            1
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        logger.info(f"Usuario registrado: {register_data.username}")
        
        # Crear token automáticamente después del registro
        access_token = create_access_token(data={"sub": user_id})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "IdUsuario": user_id,
                "Username": register_data.username,
                "Email": register_data.email,
                "Rol": register_data.rol
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en registro: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
    finally:
        if conn:
            conn.close()


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """Obtener información del usuario actual"""
    return {
        "IdUsuario": current_user["IdUsuario"],
        "Username": current_user["Username"],
        "Email": current_user["Email"],
        "Rol": current_user["Rol"]
    }

