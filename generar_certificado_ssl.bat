@echo off
REM Script para generar certificado SSL autofirmado en Windows

echo Generando certificado SSL autofirmado para desarrollo local...

REM Crear directorio para certificados
if not exist certs mkdir certs
cd certs

REM Generar certificado autofirmado
openssl req -x509 -newkey rsa:4096 -nodes -keyout key.pem -out cert.pem -days 365 -subj "/C=DO/ST=Distrito Nacional/L=Santo Domingo/O=Clinica Medica/CN=localhost"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Certificado generado exitosamente en: certs\
    echo    - cert.pem (certificado)
    echo    - key.pem (clave privada)
    echo.
    echo Para usar HTTPS, ejecuta:
    echo   uvicorn main:app --reload --host 0.0.0.0 --port 8443 --ssl-keyfile certs/key.pem --ssl-certfile certs/cert.pem
) else (
    echo.
    echo ERROR: No se pudo generar el certificado.
    echo Asegurate de tener OpenSSL instalado.
    echo.
    echo Puedes descargarlo de: https://slproweb.com/products/Win32OpenSSL.html
)

cd ..

