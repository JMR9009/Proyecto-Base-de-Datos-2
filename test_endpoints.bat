@echo off
REM Script para probar los endpoints de la API

echo.
echo ==================== PRUEBA DE ENDPOINTS ====================
echo.

REM Endpoint raíz
echo [1] Probando GET /
curl -s http://127.0.0.1:8000/
echo.
echo.

REM Health check
echo [2] Probando GET /health
curl -s http://127.0.0.1:8000/health
echo.
echo.

REM Obtener pacientes
echo [3] Probando GET /pacientes/
curl -s http://127.0.0.1:8000/pacientes/
echo.
echo.

REM Obtener médicos
echo [4] Probando GET /medicos/
curl -s http://127.0.0.1:8000/medicos/
echo.
echo.

REM Obtener citas
echo [5] Probando GET /citas/
curl -s http://127.0.0.1:8000/citas/
echo.
echo.

echo ==================== DOCUMENTACIÓN ====================
echo.
echo Swagger UI:  http://127.0.0.1:8000/docs
echo ReDoc:       http://127.0.0.1:8000/redoc
echo.
