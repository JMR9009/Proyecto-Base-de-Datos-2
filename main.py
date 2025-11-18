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
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001",  # Puerto alternativo del frontend
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
        "https://localhost:3000",  # HTTPS en desarrollo
        "https://localhost:3001",
        "https://localhost:5173"
    ] if not IS_PRODUCTION else [],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],  # Incluir OPTIONS para preflight
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],  # Headers necesarios
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset", "X-Process-Time"]
)

# Inicializar base de datos al iniciar la aplicación
init_db()

# Inicializar usuario administrador
from init_admin import init_admin_user
init_admin_user()

# Incluir routers
from routers import (
    paciente_router, medico_router, departamento_router, puesto_router, 
    asignacion_router, contrato_router, capacitacion_router, asignacion_capacitacion_router,
    evaluacion_desempeno_router, criterio_evaluacion_router, concepto_nomina_router, nomina_router,
    vacacion_router, permiso_router, balance_vacacion_router, documento_router, version_documento_router,
    categoria_documento_router, historial_documento_router, usuario_router, rol_router, historial_usuario_router
)

app.include_router(cita_router.router)
app.include_router(auth_router.router)
app.include_router(empleado_router.router)
app.include_router(asistencia_router.router)
app.include_router(paciente_router.router)
app.include_router(medico_router.router)
app.include_router(departamento_router.router)
app.include_router(puesto_router.router)
app.include_router(asignacion_router.router)
app.include_router(contrato_router.router)
app.include_router(capacitacion_router.router)
app.include_router(asignacion_capacitacion_router.router)
app.include_router(evaluacion_desempeno_router.router)
app.include_router(criterio_evaluacion_router.router)
app.include_router(concepto_nomina_router.router)
app.include_router(nomina_router.router)
app.include_router(vacacion_router.router)
app.include_router(permiso_router.router)
app.include_router(balance_vacacion_router.router)
app.include_router(documento_router.router)
app.include_router(version_documento_router.router)
app.include_router(categoria_documento_router.router)
app.include_router(historial_documento_router.router)
app.include_router(usuario_router.router)
app.include_router(rol_router.router)
app.include_router(historial_usuario_router.router)

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
