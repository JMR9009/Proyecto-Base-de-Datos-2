# 🔒 Configuración HTTPS - Guía de Implementación

## 📋 Estado Actual

**Protocolo actual**: HTTP (desarrollo local)
**Estado**: ✅ Funcional para desarrollo
**Recomendación**: HTTPS necesario para producción

## ⚠️ Importante: HTTP vs HTTPS

### Desarrollo Local (HTTP)
- ✅ **Está bien usar HTTP** en desarrollo local
- ✅ La aplicación funciona correctamente con HTTP
- ✅ Todos los middlewares de seguridad funcionan con HTTP
- ⚠️ Solo el header HSTS se omite automáticamente en HTTP

### Producción (HTTPS)
- 🔒 **HTTPS es OBLIGATORIO** en producción
- 🔒 Protege datos sensibles en tránsito
- 🔒 Requerido por navegadores modernos
- 🔒 Necesario para cumplir estándares de seguridad

## 🚀 Opciones para Implementar HTTPS

### Opción 1: Usar un Proxy Reverso (Recomendado)

#### Con Nginx
```nginx
server {
    listen 443 ssl http2;
    server_name api.tudominio.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Con Caddy (Automático con Let's Encrypt)
```caddy
api.tudominio.com {
    reverse_proxy localhost:8000
}
```

### Opción 2: Certificado SSL Directo en FastAPI

#### Instalar dependencias
```bash
pip install uvicorn[standard]
```

#### Ejecutar con SSL
```bash
uvicorn main:app \
    --host 0.0.0.0 \
    --port 8443 \
    --ssl-keyfile /path/to/key.pem \
    --ssl-certfile /path/to/cert.pem
```

### Opción 3: Usar Let's Encrypt (Gratis)

#### Con Certbot
```bash
# Instalar certbot
sudo apt-get install certbot

# Obtener certificado
sudo certbot certonly --standalone -d api.tudominio.com

# Los certificados estarán en:
# /etc/letsencrypt/live/api.tudominio.com/fullchain.pem
# /etc/letsencrypt/live/api.tudominio.com/privkey.pem
```

## 🔧 Configuración Actual (HTTP)

La aplicación está configurada para funcionar con HTTP en desarrollo:

```python
# En middleware.py
is_https = request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https"
is_production = os.getenv("ENVIRONMENT", "development").lower() == "production"

# HSTS solo se agrega si:
# - La conexión es HTTPS, O
# - Está en modo producción (preparado para HTTPS)
if is_https or is_production:
    response.headers["Strict-Transport-Security"] = "..."
```

## 📝 Variables de Entorno

### Desarrollo (HTTP)
```bash
# No necesitas configurar nada especial
# La app funciona con HTTP por defecto
uvicorn main:app --reload --port 8000
```

### Producción (HTTPS)
```bash
# Configurar entorno de producción
export ENVIRONMENT=production

# Con proxy reverso (recomendado)
uvicorn main:app --host 0.0.0.0 --port 8000

# O directamente con SSL
uvicorn main:app \
    --host 0.0.0.0 \
    --port 8443 \
    --ssl-keyfile /path/to/key.pem \
    --ssl-certfile /path/to/cert.pem
```

## 🔐 Headers de Seguridad con HTTP vs HTTPS

### Con HTTP (Desarrollo)
- ✅ `X-Content-Type-Options`: ✅ Activo
- ✅ `X-Frame-Options`: ✅ Activo
- ✅ `X-XSS-Protection`: ✅ Activo
- ✅ `Referrer-Policy`: ✅ Activo
- ✅ `Permissions-Policy`: ✅ Activo
- ⚠️ `Strict-Transport-Security`: ⚠️ Omitido (correcto para HTTP)

### Con HTTPS (Producción)
- ✅ Todos los headers anteriores: ✅ Activos
- ✅ `Strict-Transport-Security`: ✅ Activo (fuerza HTTPS)

## ✅ Verificación

### Verificar Headers de Seguridad
```bash
# Con HTTP
curl -I http://localhost:8000/health

# Con HTTPS
curl -I https://api.tudominio.com/health
```

### Verificar que HSTS solo aparece en HTTPS
```bash
# HTTP - NO debe tener HSTS
curl -I http://localhost:8000/health | grep -i "strict-transport"

# HTTPS - DEBE tener HSTS
curl -I https://api.tudominio.com/health | grep -i "strict-transport"
```

## 🎯 Recomendación Final

**Para desarrollo local**: 
- ✅ Continúa usando HTTP - está perfecto
- ✅ Todos los middlewares funcionan correctamente
- ✅ La seguridad está implementada correctamente

**Para producción**:
- 🔒 Implementa HTTPS usando un proxy reverso (Nginx/Caddy)
- 🔒 Usa Let's Encrypt para certificados gratuitos
- 🔒 Configura `ENVIRONMENT=production`
- 🔒 El header HSTS se activará automáticamente

## 📚 Recursos Adicionales

- [Let's Encrypt](https://letsencrypt.org/)
- [Nginx SSL Configuration](https://nginx.org/en/docs/http/configuring_https_servers.html)
- [Caddy Automatic HTTPS](https://caddyserver.com/docs/automatic-https)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

## ⚡ Nota Importante

La aplicación **ya está preparada** para HTTPS. Solo necesitas:
1. Configurar un proxy reverso con SSL, O
2. Ejecutar uvicorn con certificados SSL

Los middlewares detectarán automáticamente HTTPS y ajustarán los headers de seguridad.

