from fastapi import FastAPI
from routers import paciente_router, medico_router, cita_router

app = FastAPI(
    title="API Clínica Médica",
    description="API para gestión de pacientes, médicos y citas",
    version="1.0.0"
)

# Incluir routers
app.include_router(paciente_router.router)
app.include_router(medico_router.router)
app.include_router(cita_router.router)


@app.get("/")
def root():
    """Endpoint raíz de la API"""
    return {
        "mensaje": "API Clínica Médica",
        "version": "1.0.0",
        "endpoints": {
            "pacientes": "/pacientes",
            "medicos": "/medicos",
            "citas": "/citas"
        }
    }