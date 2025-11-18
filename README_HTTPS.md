# 🔒 Configuración HTTPS - Guía Rápida

## ✅ Lo que ya está configurado

- ✅ Middleware detecta HTTPS automáticamente
- ✅ Headers de seguridad se ajustan con HTTPS
- ✅ CORS permite conexiones HTTPS
- ✅ Scripts para generar certificados

## 🚀 Inicio Rápido

### Opción 1: Generar Certificado con Python (Recomendado)

```bash
# Instalar dependencia
pip install cryptography

# Generar certificado
python generar_certificado_python.py
```

### Opción 2: Generar Certificado con OpenSSL

**Windows:**
```bash
generar_certificado_ssl.bat
```

**Linux/Mac:**
```bash
bash generar_certificado_ssl.sh
```

### Iniciar Servidor con HTTPS

```bash
# Opción automática (detecta HTTP o HTTPS)
python iniciar_servidor.py

# O manualmente con HTTPS
python iniciar_https.py

# O con uvicorn directamente
uvicorn main:app --reload --host 0.0.0.0 --port 8443 \
    --ssl-keyfile certs/key.pem --ssl-certfile certs/cert.pem
```

## 📍 URLs

**Con HTTP (desarrollo):**
- Backend: http://localhost:8000
- Docs: http://localhost:8000/docs

**Con HTTPS (desarrollo):**
- Backend: https://localhost:8443
- Docs: https://localhost:8443/docs
- ⚠️ El navegador mostrará advertencia (normal para certificados autofirmados)

## 🔧 Configuración del Frontend

El frontend ya está configurado para usar HTTPS automáticamente.

**Para desarrollo local con HTTPS:**
1. Genera los certificados (ver arriba)
2. Inicia el backend con HTTPS (puerto 8443)
3. Actualiza `vite.config.ts` si es necesario:

```typescript
proxy: {
  '/api': {
    target: 'https://127.0.0.1:8443',  // Cambiar a HTTPS
    secure: false,  // Para certificados autofirmados
    // ...
  }
}
```

## 🎯 Verificación

```bash
# Verificar que HTTPS funciona
curl -k https://localhost:8443/health

# Verificar headers de seguridad
curl -kI https://localhost:8443/health | grep -i "strict-transport"
```

## 📝 Notas Importantes

1. **Certificados autofirmados**: Solo para desarrollo. En producción usa Let's Encrypt.
2. **Advertencia del navegador**: Es normal con certificados autofirmados. Acepta la excepción.
3. **Puerto**: HTTPS usa puerto 8443 para evitar conflictos con HTTP (8000).
4. **Middleware**: Detecta HTTPS automáticamente y activa HSTS.

## 🚀 Producción

Para producción, usa un proxy reverso (Nginx/Caddy) con Let's Encrypt.
Ver `GUIA_HTTPS_SEGURIDAD.md` para detalles completos.

