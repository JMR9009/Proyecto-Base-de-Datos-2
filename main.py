from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional
from routers import cita_router, auth_router, asistencia_router, empleado_router
from database import get_db_connection, init_db
from security import sanitize_string, validate_phone, validate_date, safe_error_message
from middleware import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    PayloadSizeMiddleware,
    ContentTypeValidationMiddleware
)
import os
import logging
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Variable de entorno para producción
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

app = FastAPI(
    title="API Clínica Médica",
    version="1.0.0",
    docs_url="/docs" if not IS_PRODUCTION else None,  # Deshabilitar docs en producción
    redoc_url="/redoc" if not IS_PRODUCTION else None
)

# Middleware de seguridad (orden importa - se ejecutan en orden inverso)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(PayloadSizeMiddleware)
app.add_middleware(ContentTypeValidationMiddleware)

# Configurar CORS de forma más segura
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"] if not IS_PRODUCTION else [],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Solo métodos necesarios
    allow_headers=["Content-Type", "Authorization"],  # Solo headers necesarios
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset", "X-Process-Time"]
)

# Inicializar base de datos al iniciar la aplicación
init_db()

# Inicializar usuario administrador
from init_admin import init_admin_user
init_admin_user()

# Incluir routers
app.include_router(cita_router.router)
app.include_router(auth_router.router)
app.include_router(empleado_router.router)
app.include_router(asistencia_router.router)


class Medico(BaseModel):
    Nombre: str = Field(..., min_length=1, max_length=100)
    Apellido: str = Field(..., min_length=1, max_length=100)
    Especialidad: str = Field(..., min_length=1, max_length=100)
    Telefono: str = Field(..., min_length=8, max_length=20)
    Email: EmailStr
    
    @validator('Nombre', 'Apellido', 'Especialidad')
    def sanitize_text(cls, v):
        return sanitize_string(v, max_length=100)
    
    @validator('Telefono')
    def validate_phone(cls, v):
        v = sanitize_string(v, max_length=20)
        if not validate_phone(v):
            raise ValueError('Formato de teléfono inválido')
        return v

class Paciente(BaseModel):
    Nombre: str = Field(..., min_length=1, max_length=100)
    Apellido: str = Field(..., min_length=1, max_length=100)
    FechaNacimiento: str = Field(..., min_length=10, max_length=10)
    Genero: str = Field(..., min_length=1, max_length=20)
    Telefono: str = Field(..., min_length=8, max_length=20)
    Email: EmailStr
    Direccion: Optional[str] = Field(None, max_length=255)
    
    @validator('Nombre', 'Apellido', 'Genero')
    def sanitize_text(cls, v):
        return sanitize_string(v, max_length=100)
    
    @validator('FechaNacimiento')
    def validate_date(cls, v):
        if not validate_date(v):
            raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD')
        return v
    
    @validator('Telefono')
    def validate_phone(cls, v):
        v = sanitize_string(v, max_length=20)
        if not validate_phone(v):
            raise ValueError('Formato de teléfono inválido')
        return v
    
    @validator('Direccion')
    def sanitize_address(cls, v):
        if v is None:
            return None
        return sanitize_string(v, max_length=255)

@app.get("/")
def root():
    return {"mensaje": "API Clínica Médica", "version": "1.0.0"}

@app.get("/health")
def health_check():
    """Endpoint de salud de la API"""
    try:
        # Verificar conexión a la base de datos
        conn = get_db_connection()
        conn.close()
        return {
            "status": "ok",
            "database": "connected",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Health check falló: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Servicio no disponible - Error en base de datos"
        )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Manejar rutas no encontradas"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Ruta no encontrada",
            "message": f"La ruta {request.url.path} no existe"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Manejar errores internos del servidor"""
    logger.error(f"Error interno en {request.url.path}: {str(exc)}", exc_info=True)
    error_msg = "Error interno del servidor" if IS_PRODUCTION else str(exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "message": error_msg
        }
    )

@app.post("/medicos")
def crear_medico(medico: Medico):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Medicos (Nombre, Apellido, Especialidad, Telefono, Email)
            VALUES (?, ?, ?, ?, ?)
        """, (medico.Nombre, medico.Apellido, medico.Especialidad, medico.Telefono, medico.Email))
        conn.commit()
        medico_id = cursor.lastrowid
        logger.info(f"Médico creado: ID {medico_id}")
        return {"mensaje": "Médico creado exitosamente", "IdMedico": medico_id}
    except Exception as e:
        logger.error(f"Error al crear médico: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

@app.get("/medicos")
def obtener_medicos():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Medicos")
        rows = cursor.fetchall()
        medicos = [dict(row) for row in rows]
        return medicos
    except Exception as e:
        logger.error(f"Error al obtener médicos: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

@app.get("/medicos/{id}")
def obtener_medico(id: int):
    if id <= 0:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Medicos WHERE IdMedico = ?", (id,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Médico no encontrado")
        medico = dict(row)
        return medico
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener médico {id}: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

@app.put("/medicos/{id}")
def actualizar_medico(id: int, medico: Medico):
    if id <= 0:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Medicos
            SET Nombre = ?, Apellido = ?, Especialidad = ?, Telefono = ?, Email = ?
            WHERE IdMedico = ?
        """, (medico.Nombre, medico.Apellido, medico.Especialidad, medico.Telefono, medico.Email, id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Médico no encontrado")
        conn.commit()
        logger.info(f"Médico actualizado: ID {id}")
        return {"mensaje": "Médico actualizado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar médico {id}: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

@app.delete("/medicos/{id}")
def eliminar_medico(id: int):
    if id <= 0:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Verificar si hay citas asociadas
        cursor.execute("SELECT COUNT(*) FROM Citas WHERE IdMedico = ?", (id,))
        citas_count = cursor.fetchone()[0]
        if citas_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"No se puede eliminar el médico porque tiene {citas_count} cita(s) asociada(s)"
            )
        
        cursor.execute("DELETE FROM Medicos WHERE IdMedico = ?", (id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Médico no encontrado")
        conn.commit()
        logger.info(f"Médico eliminado: ID {id}")
        return {"mensaje": "Médico eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar médico {id}: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

# Endpoints de Pacientes
@app.get("/pacientes")
def obtener_pacientes():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Pacientes")
        rows = cursor.fetchall()
        pacientes = [dict(row) for row in rows]
        return pacientes
    except Exception as e:
        logger.error(f"Error al obtener pacientes: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

@app.get("/pacientes/{id}")
def obtener_paciente(id: int):
    if id <= 0:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Pacientes WHERE IdPaciente = ?", (id,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        paciente = dict(row)
        return paciente
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener paciente {id}: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

@app.post("/pacientes")
def crear_paciente(paciente: Paciente):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Pacientes (Nombre, Apellido, FechaNacimiento, Genero, Telefono, Email, Direccion)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (paciente.Nombre, paciente.Apellido, paciente.FechaNacimiento, 
             paciente.Genero, paciente.Telefono, paciente.Email, paciente.Direccion))
        conn.commit()
        paciente_id = cursor.lastrowid
        logger.info(f"Paciente creado: ID {paciente_id}")
        return {"mensaje": "Paciente creado exitosamente", "IdPaciente": paciente_id}
    except Exception as e:
        logger.error(f"Error al crear paciente: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

@app.put("/pacientes/{id}")
def actualizar_paciente(id: int, paciente: Paciente):
    if id <= 0:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Pacientes
            SET Nombre = ?, Apellido = ?, FechaNacimiento = ?, Genero = ?, 
                Telefono = ?, Email = ?, Direccion = ?
            WHERE IdPaciente = ?
        """, (paciente.Nombre, paciente.Apellido, paciente.FechaNacimiento, 
             paciente.Genero, paciente.Telefono, paciente.Email, paciente.Direccion, id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        conn.commit()
        logger.info(f"Paciente actualizado: ID {id}")
        return {"mensaje": "Paciente actualizado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar paciente {id}: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()

@app.delete("/pacientes/{id}")
def eliminar_paciente(id: int):
    if id <= 0:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Verificar si hay citas asociadas
        cursor.execute("SELECT COUNT(*) FROM Citas WHERE IdPaciente = ?", (id,))
        citas_count = cursor.fetchone()[0]
        if citas_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"No se puede eliminar el paciente porque tiene {citas_count} cita(s) asociada(s)"
            )
        
        cursor.execute("DELETE FROM Pacientes WHERE IdPaciente = ?", (id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        conn.commit()
        logger.info(f"Paciente eliminado: ID {id}")
        return {"mensaje": "Paciente eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar paciente {id}: {str(e)}", exc_info=True)
        error_msg = safe_error_message(e, IS_PRODUCTION)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if conn:
            conn.close()