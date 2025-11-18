# 🔒 Seguridad de la API - Documentación Completa

## 🛡️ Middleware de Seguridad Implementado

### 1. SecurityHeadersMiddleware
**Propósito**: Agregar headers de seguridad HTTP estándar

**Headers agregados**:
- `X-Content-Type-Options: nosniff` - Previene MIME type sniffing
- `X-Frame-Options: DENY` - Previene clickjacking
- `X-XSS-Protection: 1; mode=block` - Protección XSS básica
- `Strict-Transport-Security` - Fuerza HTTPS (HSTS)
- `Referrer-Policy: strict-origin-when-cross-origin` - Controla información del referrer
- `Permissions-Policy` - Deshabilita geolocalización, micrófono, cámara

**Archivo**: `middleware.py`

### 2. RateLimitMiddleware
**Propósito**: Prevenir abuso de la API limitando requests por IP

**Configuración**:
- Límite: 100 requests por minuto por IP
- Ventana: 60 segundos
- Headers de respuesta:
  - `X-RateLimit-Limit`: Límite total
  - `X-RateLimit-Remaining`: Requests restantes
  - `X-RateLimit-Reset`: Timestamp de reset

**Respuesta cuando se excede**:
- Status: `429 Too Many Requests`
- Mensaje informativo

**Archivo**: `middleware.py`

### 3. RequestLoggingMiddleware
**Propósito**: Registrar todas las requests para auditoría y debugging

**Registra**:
- Requests con errores (status >= 400)
- Requests lentas (> 1 segundo)
- IP del cliente
- Método HTTP y ruta
- Tiempo de procesamiento

**Header agregado**:
- `X-Process-Time`: Tiempo de procesamiento en segundos

**Archivo**: `middleware.py`

### 4. PayloadSizeMiddleware
**Propósito**: Prevenir ataques de payload grande

**Límite**:
- Tamaño máximo: 1MB por request

**Respuesta cuando se excede**:
- Status: `413 Request Entity Too Large`
- Mensaje informativo

**Archivo**: `middleware.py`

### 5. ContentTypeValidationMiddleware
**Propósito**: Validar Content-Type en requests con body

**Tipos permitidos**:
- `application/json`
- `multipart/form-data`
- `application/x-www-form-urlencoded`

**Respuesta cuando es inválido**:
- Status: `415 Unsupported Media Type`
- Mensaje informativo

**Archivo**: `middleware.py`

## 🔐 Configuración CORS Mejorada

```python
allow_origins=["http://localhost:3000", "http://localhost:5173"]  # Solo en desarrollo
allow_methods=["GET", "POST", "PUT", "DELETE"]  # Solo métodos necesarios
allow_headers=["Content-Type", "Authorization"]  # Solo headers necesarios
```

**En producción**: `allow_origins=[]` (configurar según necesidad)

## 🚫 Protección de Documentación

En producción, los endpoints de documentación están deshabilitados:
- `/docs` (Swagger UI) - Deshabilitado
- `/redoc` (ReDoc) - Deshabilitado

**Configuración**: Basada en variable de entorno `ENVIRONMENT`

## 📊 Endpoints de Seguridad

### GET /health
Endpoint de salud que verifica:
- Estado de la API
- Conexión a la base de datos
- Timestamp de respuesta

**Uso**: Monitoreo y health checks

## ⚠️ Manejo de Errores Mejorado

### 404 Not Found
- Handler personalizado para rutas no encontradas
- Mensaje informativo sin exponer estructura interna

### 500 Internal Server Error
- Handler personalizado para errores internos
- En producción: mensaje genérico
- En desarrollo: detalles del error
- Logging completo del error

## 🔍 Validaciones Implementadas

### Nivel de Request
1. ✅ Validación de Content-Type
2. ✅ Validación de tamaño de payload
3. ✅ Rate limiting por IP
4. ✅ Logging de requests sospechosas

### Nivel de Datos
1. ✅ Validación con Pydantic
2. ✅ Sanitización de strings
3. ✅ Validación de formato (email, teléfono, fecha)
4. ✅ Límites de longitud
5. ✅ Validación de IDs (> 0)

### Nivel de Base de Datos
1. ✅ Parámetros preparados (SQL injection)
2. ✅ Validación de integridad referencial
3. ✅ Manejo seguro de conexiones

## 📈 Métricas y Monitoreo

### Headers de Respuesta Útiles
- `X-Process-Time`: Tiempo de procesamiento
- `X-RateLimit-Limit`: Límite de rate limit
- `X-RateLimit-Remaining`: Requests restantes
- `X-RateLimit-Reset`: Timestamp de reset

### Logging
- Nivel INFO: Operaciones importantes y errores
- Nivel WARNING: Rate limit excedido, payload grande
- Nivel ERROR: Errores de aplicación y base de datos

## 🚀 Configuración de Producción

### Variables de Entorno

```bash
# Activar modo producción
export ENVIRONMENT=production

# Configurar rate limits (opcional)
export RATE_LIMIT_REQUESTS=100
export RATE_LIMIT_WINDOW=60

# Configurar tamaño máximo de payload (opcional)
export MAX_PAYLOAD_SIZE=1048576  # 1MB en bytes
```

### Recomendaciones Adicionales

1. **HTTPS**: Usar siempre HTTPS en producción
2. **Firewall**: Configurar firewall para limitar acceso
3. **WAF**: Considerar Web Application Firewall
4. **Monitoreo**: Implementar sistema de monitoreo (Sentry, Datadog, etc.)
5. **Backup**: Backup regular de la base de datos
6. **Autenticación**: Implementar autenticación JWT o OAuth2
7. **API Keys**: Considerar API keys para acceso externo

## 🔐 Nivel de Seguridad Actual

**Nivel**: 🟢 **Alto** (para API pública sin autenticación)

- ✅ Headers de seguridad: Excelente
- ✅ Rate limiting: Implementado
- ✅ Validación de entrada: Excelente
- ✅ Protección contra inyección: Excelente
- ✅ Manejo de errores: Excelente
- ⚠️ Autenticación: No implementada (recomendado para producción)
- ⚠️ Autorización: No implementada (recomendado para producción)

## 📝 Checklist de Seguridad

- [x] Headers de seguridad HTTP
- [x] Rate limiting
- [x] Validación de Content-Type
- [x] Límite de tamaño de payload
- [x] Logging de seguridad
- [x] Manejo seguro de errores
- [x] CORS configurado correctamente
- [x] Documentación deshabilitada en producción
- [ ] Autenticación (recomendado)
- [ ] Autorización por roles (recomendado)
- [ ] Encriptación de datos sensibles (recomendado)
- [ ] WAF (recomendado para producción)

## 🐛 Pruebas de Seguridad

### Probar Rate Limiting
```bash
# Hacer 101 requests rápidas
for i in {1..101}; do curl http://localhost:8000/health; done
# La request 101 debería retornar 429
```

### Probar Payload Grande
```bash
# Crear archivo grande y enviarlo
dd if=/dev/zero of=large.txt bs=1M count=2
curl -X POST http://localhost:8000/pacientes \
  -H "Content-Type: application/json" \
  -d @large.txt
# Debería retornar 413
```

### Probar Content-Type Inválido
```bash
curl -X POST http://localhost:8000/pacientes \
  -H "Content-Type: text/plain" \
  -d "test"
# Debería retornar 415
```

