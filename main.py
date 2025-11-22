from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import paciente_router, medico_router, cita_router, producto_router
from config import settings




app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(paciente_router.router)
app.include_router(medico_router.router)
app.include_router(cita_router.router)
app.include_router(producto_router.router)




@app.get("/")
def root():
    """Endpoint raíz de la API"""
    return {
        "mensaje": settings.API_TITLE,
        "version": settings.API_VERSION,
        "documentacion": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "pacientes": "/pacientes",
            "medicos": "/medicos",
            "citas": "/citas",
            "productos": "/productos"
            
            
        }
    }


@app.get("/health")
def health_check():
    """Endpoint para verificar el estado de la API"""
    try:
        from database import Database
        Database.get_connection().close()
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }