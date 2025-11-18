# 🔒 Ejemplo Práctico: Configuración HTTPS

## 📍 Cómo se Detecta HTTPS en el Código Actual

### Archivo: `middleware.py` (líneas 28-30)

```python
# Detección automática de HTTPS
is_https = (
    request.url.scheme == "https" or  # Conexión directa HTTPS
    request.headers.get("x-forwarded-proto") == "https"  # Proxy reverso
)
```

**Cómo funciona:**
- Si FastAPI recibe conexión HTTPS directa → `request.url.scheme == "https"`
- Si hay proxy reverso (Nginx/Caddy) → El proxy envía `X-Forwarded-Proto: https`
- El middleware detecta automáticamente y activa HSTS

## 🚀 Configuración Paso a Paso

### Escenario 1: Desarrollo Local (HTTP) - Actual

**Backend:**
```bash
cd Proyecto-Base-de-Datos-2
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# → http://localhost:8000
```

**Frontend:**
```bash
cd frontend-citasmedicas
npm run dev
# → http://localhost:3000
```

**Estado:** ✅ Funciona correctamente con HTTP

---

### Escenario 2: Producción con Nginx + Let's Encrypt

#### Paso 1: Instalar Nginx

```bash
sudo apt-get update
sudo apt-get install nginx
```

#### Paso 2: Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/api-clinica
```

**Contenido del archivo:**

```nginx
# Redirigir HTTP a HTTPS
server {
    listen 80;
    server_name api.tudominio.com;
    return 301 https://$server_name$request_uri;
}

# Servidor HTTPS
server {
    listen 443 ssl http2;
    server_name api.tudominio.com;

    # Certificados SSL (se obtendrán con Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.tudominio.com/privkey.pem;

    # Configuración SSL moderna
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Headers de seguridad
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;

    # Proxy a FastAPI
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;  # ← CRÍTICO: Permite detectar HTTPS
        proxy_set_header X-Forwarded-Host $host;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

#### Paso 3: Habilitar el sitio

```bash
sudo ln -s /etc/nginx/sites-available/api-clinica /etc/nginx/sites-enabled/
sudo nginx -t  # Verificar configuración
sudo systemctl reload nginx
```

#### Paso 4: Obtener Certificado SSL

```bash
# Instalar certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtener certificado (certbot configurará Nginx automáticamente)
sudo certbot --nginx -d api.tudominio.com

# Verificar renovación automática
sudo certbot renew --dry-run
```

#### Paso 5: Verificar

```bash
# Probar HTTPS
curl https://api.tudominio.com/health

# Verificar headers
curl -I https://api.tudominio.com/health | grep -i "strict-transport"
```

---

### Escenario 3: Desarrollo Local con HTTPS (Opcional)

#### Generar Certificado Autofirmado

```bash
# Crear directorio para certificados
mkdir -p Proyecto-Base-de-Datos-2/certs
cd Proyecto-Base-de-Datos-2/certs

# Generar certificado autofirmado
openssl req -x509 -newkey rsa:4096 -nodes \
    -keyout key.pem \
    -out cert.pem \
    -days 365 \
    -subj "/CN=localhost"

# Dar permisos
chmod 600 key.pem cert.pem
```

#### Ejecutar Backend con HTTPS

```bash
cd Proyecto-Base-de-Datos-2
uvicorn main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8443 \
    --ssl-keyfile certs/key.pem \
    --ssl-certfile certs/cert.pem
```

**Acceso:** `https://localhost:8443` (navegador mostrará advertencia de certificado autofirmado)

#### Actualizar Frontend

```typescript
// vite.config.ts
proxy: {
  '/api': {
    target: 'https://localhost:8443',  // ← Cambiar a HTTPS
    changeOrigin: true,
    secure: false,  // ← false para certificados autofirmados
    rewrite: (path) => path.replace(/^\/api/, ''),
  }
}
```

---

## 🔍 Verificación de HTTPS

### 1. Verificar que el Middleware Detecta HTTPS

**Con proxy reverso:**
```bash
# El proxy debe enviar este header:
X-Forwarded-Proto: https
```

**El middleware lo detecta:**
```python
# middleware.py línea 29
is_https = request.headers.get("x-forwarded-proto") == "https"
```

### 2. Verificar Headers de Seguridad

```bash
# Debe incluir Strict-Transport-Security
curl -I https://api.tudominio.com/health

# Respuesta esperada:
# HTTP/1.1 200 OK
# Strict-Transport-Security: max-age=31536000; includeSubDomains
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# ...
```

### 3. Verificar en el Navegador

1. Abre `https://api.tudominio.com/docs`
2. Verifica el candado verde 🔒
3. Abre DevTools → Network → Headers
4. Busca `Strict-Transport-Security`

## 🛡️ Protección que Proporciona HTTPS

### 1. Encriptación de Datos

**Sin HTTPS:**
```
Cliente → [Datos en texto plano] → Servidor
GET /auth/login
Body: {"username": "admin", "password": "admin123"}
```

**Con HTTPS:**
```
Cliente → [Datos encriptados con TLS] → Servidor
GET /auth/login
Body: [Encriptado: no se puede leer sin la clave]
```

### 2. Protección de Tokens JWT

**Sin HTTPS:**
- ❌ Token visible: `Authorization: Bearer eyJhbGciOiJIUzI1NiIs...`
- ❌ Puede ser interceptado
- ❌ Vulnerable a man-in-the-middle

**Con HTTPS:**
- ✅ Token encriptado en tránsito
- ✅ No puede ser interceptado
- ✅ Protegido contra ataques

### 3. Integridad de Datos

- ✅ Los datos no pueden ser modificados en tránsito
- ✅ Protección contra ataques de manipulación
- ✅ Verificación de autenticidad del servidor

## 📋 Checklist de Implementación

### Backend
- [ ] Middleware detecta HTTPS automáticamente ✅ (Ya implementado)
- [ ] HSTS se activa con HTTPS ✅ (Ya implementado)
- [ ] Headers de seguridad funcionan ✅ (Ya implementado)

### Infraestructura
- [ ] Proxy reverso configurado (Nginx/Caddy)
- [ ] Certificado SSL obtenido (Let's Encrypt)
- [ ] Renovación automática configurada
- [ ] Redirección HTTP → HTTPS configurada
- [ ] Header `X-Forwarded-Proto` configurado

### Frontend
- [ ] `baseURL` actualizado a HTTPS
- [ ] Proxy de Vite configurado para HTTPS
- [ ] Certificados verificados

## 🎯 Resumen

**Estado Actual:**
- ✅ El código está **preparado para HTTPS**
- ✅ El middleware **detecta HTTPS automáticamente**
- ✅ Los headers de seguridad se **ajustan automáticamente**

**Para Activar HTTPS:**
1. Configura proxy reverso (Nginx/Caddy)
2. Obtén certificado SSL (Let's Encrypt)
3. El código detectará HTTPS automáticamente
4. HSTS se activará automáticamente

**No necesitas cambiar código**, solo configurar la infraestructura.

