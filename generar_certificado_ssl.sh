#!/bin/bash
# Script para generar certificado SSL autofirmado para desarrollo local

echo "Generando certificado SSL autofirmado para desarrollo local..."

# Crear directorio para certificados
mkdir -p certs
cd certs

# Generar certificado autofirmado válido por 365 días
openssl req -x509 -newkey rsa:4096 -nodes \
    -keyout key.pem \
    -out cert.pem \
    -days 365 \
    -subj "/C=DO/ST=Distrito Nacional/L=Santo Domingo/O=Clinica Medica/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,DNS:127.0.0.1,IP:127.0.0.1"

# Dar permisos seguros
chmod 600 key.pem cert.pem

echo "✅ Certificado generado exitosamente en: certs/"
echo "   - cert.pem (certificado)"
echo "   - key.pem (clave privada)"
echo ""
echo "Para usar HTTPS, ejecuta:"
echo "  uvicorn main:app --reload --host 0.0.0.0 --port 8443 --ssl-keyfile certs/key.pem --ssl-certfile certs/cert.pem"

