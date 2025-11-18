# 🔒 Guía Completa: HTTPS para Seguridad

## 📋 Estado Actual del Proyecto

### Desarrollo (HTTP)
- ✅ **Actualmente usando HTTP** en desarrollo local
- ✅ Funciona correctamente para desarrollo
- ✅ Middlewares de seguridad activos (excepto HSTS)

### Producción (HTTPS)
- 🔒 **HTTPS es OBLIGATORIO** para producción
- 🔒 Protege tokens JWT en tránsito
- 🔒 Protege datos sensibles
- 🔒 Requerido por navegadores modernos

## 🔍 Cómo el Backend Detecta HTTPS

### Archivo: `middleware.py` (líneas 28-40)

```python
# Detecta automáticamente si se usa HTTPS
is_https = (
    request.url.scheme == "https" or  # Conexión directa HTTPS
    request.headers.get("x-forwarded-proto") == "https"  # Proxy reverso con HTTPS
)

# HSTS solo se agrega en HTTPS o producción
if is_https or is_production:
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
```

**Cómo funciona:**
1. Si la conexión es directamente HTTPS → `request.url.scheme == "https"`
2. Si hay un proxy reverso (Nginx/Caddy) → `x-forwarded-proto: https`
3. El middleware detecta automáticamente y ajusta los headers

## 🚀 Opciones para Implementar HTTPS

### Opción 1: Proxy Reverso con Nginx (Recomendado para Producción)

#### Ventajas:
- ✅ Mejor rendimiento
- ✅ Manejo de SSL/TLS optimizado
- ✅ Balanceador de carga
- ✅ Compresión y caché

#### Configuración Nginx:

```nginx
# /etc/nginx/sites-available/api-clinica
server {
    listen 80;
    server_name api.tudominio.com;
    
    # Redirigir HTTP a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.tudominio.com;

    # Certificados SSL (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.tudominio.com/privkey.pem;
    
    # Configuración SSL moderna
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Headers de seguridad
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;  # ← Esto permite que FastAPI detecte HTTPS
        proxy_set_header X-Forwarded-Host $host;
    }
}
```

#### Obtener Certificado con Let's Encrypt:

```bash
# Instalar certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d api.tudominio.com

# Renovación automática (ya configurada)
sudo certbot renew --dry-run
```

---

### Opción 2: Caddy (Más Fácil - HTTPS Automático)

#### Ventajas:
- ✅ HTTPS automático con Let's Encrypt
- ✅ Renovación automática
- ✅ Configuración simple

#### Configuración Caddy:

```caddy
# Caddyfile
api.tudominio.com {
    reverse_proxy localhost:8000 {
        header_up X-Forwarded-Proto {scheme}
        header_up X-Forwarded-Host {host}
    }
}
```

Caddy automáticamente:
- ✅ Obtiene certificado SSL de Let's Encrypt
- ✅ Renueva certificados automáticamente
- ✅ Redirige HTTP a HTTPS
- ✅ Configura SSL/TLS óptimo

---

### Opción 3: HTTPS Directo en Uvicorn (Solo para Pruebas)

#### ⚠️ No recomendado para producción

```bash
# Generar certificado autofirmado (solo para pruebas)
openssl req -x509 -newkey rsa:4096 -nodes \
    -keyout key.pem \
    -out cert.pem \
    -days 365 \
    -subj "/CN=localhost"

# Ejecutar con SSL
uvicorn main:app \
    --host 0.0.0.0 \
    --port 8443 \
    --ssl-keyfile key.pem \
    --ssl-certfile cert.pem
```

**Acceso:** `https://localhost:8443`

---

## 🔐 Headers de Seguridad con HTTPS

### Con HTTP (Desarrollo)
```http
HTTP/1.1 200 OK
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
# ⚠️ NO hay Strict-Transport-Security (correcto para HTTP)
```

### Con HTTPS (Producción)
```http
HTTP/1.1 200 OK
Strict-Transport-Security: max-age=31536000; includeSubDomains  # ← Solo en HTTPS
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

## 📝 Configuración del Frontend para HTTPS

### Actualizar `vite.config.ts`:

```typescript
// frontend-citasmedicas/vite.config.ts
export default defineConfig({
  server: {
    port: 3000,
    host: '0.0.0.0',
    https: true,  // ← Habilitar HTTPS en desarrollo (opcional)
    proxy: {
      '/api': {
        target: 'https://api.tudominio.com',  // ← Cambiar a HTTPS en producción
        changeOrigin: true,
        secure: true,  // ← Verificar certificado SSL
        rewrite: (path) => path.replace(/^\/api/, ''),
      }
    }
  }
})
```

### Actualizar `api.ts`:

```typescript
// frontend-citasmedicas/src/services/api.ts
const baseURL = import.meta.env.VITE_API_URL || 
  (import.meta.env.PROD ? 'https://api.tudominio.com' : '/api')
```

## 🧪 Verificar que HTTPS Funciona

### 1. Verificar Certificado SSL

```bash
# Verificar certificado
openssl s_client -connect api.tudominio.com:443 -servername api.tudominio.com

# Verificar con curl
curl -vI https://api.tudominio.com/health
```

### 2. Verificar Headers de Seguridad

```bash
# Debe incluir Strict-Transport-Security
curl -I https://api.tudominio.com/health | grep -i "strict-transport"
```

### 3. Verificar en el Navegador

1. Abre `https://api.tudominio.com/docs`
2. Verifica el candado verde en la barra de direcciones
3. Abre DevTools → Network → Headers
4. Verifica que `Strict-Transport-Security` esté presente

## 🔄 Migración de HTTP a HTTPS

### Paso 1: Configurar Proxy Reverso

```bash
# Instalar Nginx
sudo apt-get install nginx

# Configurar sitio (ver configuración arriba)
sudo nano /etc/nginx/sites-available/api-clinica
sudo ln -s /etc/nginx/sites-available/api-clinica /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Paso 2: Obtener Certificado SSL

```bash
# Con Let's Encrypt
sudo certbot --nginx -d api.tudominio.com
```

### Paso 3: Actualizar Backend

```bash
# No necesitas cambiar nada en el código
# El middleware detecta HTTPS automáticamente
# Solo asegúrate de que el proxy envíe X-Forwarded-Proto
```

### Paso 4: Actualizar Frontend

```typescript
// Cambiar baseURL a HTTPS
const baseURL = 'https://api.tudominio.com'
```

### Paso 5: Verificar

```bash
# Probar endpoint
curl https://api.tudominio.com/health

# Verificar headers
curl -I https://api.tudominio.com/health
```

## 🛡️ Seguridad Adicional con HTTPS

### 1. HSTS (HTTP Strict Transport Security)

**Ya implementado en `middleware.py`:**
```python
if is_https or is_production:
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
```

**Qué hace:**
- Fuerza al navegador a usar HTTPS siempre
- Previene ataques de downgrade
- Protege contra cookies hijacking

### 2. Protección de Tokens JWT

**Con HTTPS:**
- ✅ Tokens JWT se transmiten encriptados
- ✅ No pueden ser interceptados
- ✅ Protección contra man-in-the-middle

**Sin HTTPS:**
- ❌ Tokens visibles en texto plano
- ❌ Vulnerables a interceptación
- ❌ Riesgo de seguridad crítico

### 3. Protección de Contraseñas

**Con HTTPS:**
- ✅ Contraseñas encriptadas en tránsito
- ✅ Login seguro
- ✅ Protección de credenciales

## 📊 Comparación: HTTP vs HTTPS

| Característica | HTTP (Desarrollo) | HTTPS (Producción) |
|----------------|-------------------|---------------------|
| **Encriptación** | ❌ No | ✅ Sí (TLS/SSL) |
| **Tokens JWT** | ⚠️ Vulnerables | ✅ Protegidos |
| **Contraseñas** | ⚠️ Vulnerables | ✅ Protegidas |
| **HSTS Header** | ❌ No aplica | ✅ Activo |
| **Certificado** | ❌ No necesario | ✅ Requerido |
| **Puerto** | 80, 8000 | 443, 8443 |
| **Uso** | Desarrollo local | Producción |

## ✅ Checklist para Implementar HTTPS

- [ ] Configurar proxy reverso (Nginx/Caddy)
- [ ] Obtener certificado SSL (Let's Encrypt)
- [ ] Configurar renovación automática de certificado
- [ ] Actualizar `vite.config.ts` para usar HTTPS
- [ ] Actualizar `baseURL` en `api.ts`
- [ ] Verificar que `X-Forwarded-Proto` se envía correctamente
- [ ] Probar endpoints con HTTPS
- [ ] Verificar headers de seguridad
- [ ] Configurar redirección HTTP → HTTPS
- [ ] Probar en navegador (candado verde)

## 🎯 Resumen

1. **Desarrollo**: HTTP está bien, la app funciona correctamente
2. **Producción**: HTTPS es OBLIGATORIO
3. **Implementación**: Usa proxy reverso (Nginx/Caddy) con Let's Encrypt
4. **Detección**: El middleware detecta HTTPS automáticamente
5. **Headers**: HSTS se activa automáticamente con HTTPS

## 📚 Recursos

- [Let's Encrypt](https://letsencrypt.org/) - Certificados SSL gratuitos
- [Nginx SSL](https://nginx.org/en/docs/http/configuring_https_servers.html)
- [Caddy HTTPS](https://caddyserver.com/docs/automatic-https)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

