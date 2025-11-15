# Script para ejecutar la API
# Activar el entorno virtual
Write-Host "Activando entorno virtual..." -ForegroundColor Green
& ".\env\Scripts\Activate.ps1"

# Ejecutar la aplicación con uvicorn
Write-Host "Iniciando API en http://localhost:8000" -ForegroundColor Cyan
Write-Host "Documentación disponible en:" -ForegroundColor Cyan
Write-Host "  - Swagger UI: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "  - ReDoc: http://localhost:8000/redoc" -ForegroundColor Yellow
Write-Host "  - Health Check: http://localhost:8000/health" -ForegroundColor Yellow

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
