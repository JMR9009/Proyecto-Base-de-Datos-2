# 🔒 Solución de Seguridad - Autenticación JWT

## ✅ Problema Identificado y Solucionado

**Problema**: El endpoint `/empleados` (y otros endpoints) estaban **públicos** sin autenticación, permitiendo acceso sin token JWT.

**Solución**: Se agregó autenticación JWT a todos los endpoints de `/empleados` y `/asistencia` usando `Depends(get_current_active_user)`.

---

## 🔐 Seguridad Implementada

### ✅ Medidas de Seguridad Aplicadas:

1. **Autenticación JWT** - Todos los endpoints requieren token válido
2. **Sanitización de Inputs** - Prevención de XSS
3. **Validación de Datos** - Con Pydantic
4. **Protección SQL Injection** - Uso de parámetros preparados
5. **Rate Limiting** - Límite de peticiones por IP
6. **Security Headers** - Headers de seguridad HTTP
7. **CORS Configurado** - Solo origenes permitidos

---

## 📋 Cómo Usar la Autenticación

### Paso 1: Obtener Token de Autenticación

**Endpoint de Login:**
```bash
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "IdUsuario": 1,
    "Username": "admin",
    "Email": "admin@example.com",
    "Rol": "admin"
  }
}
```

### Paso 2: Usar el Token en las Peticiones

**Incluir el token en el header `Authorization`:**

```bash
GET http://localhost:8000/empleados
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ejemplo con curl:**
```bash
curl -X GET "http://localhost:8000/empleados" \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

**Ejemplo con JavaScript/Axios:**
```javascript
axios.get('http://localhost:8000/empleados', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

---

## 🚨 Errores Comunes y Soluciones

### Error 1: `{"detail":"Not Found"}`

**Causa**: El servidor no se ha reiniciado después de agregar los routers.

**Solución**:
1. Detener el servidor (Ctrl + C)
2. Reiniciar: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`

### Error 2: `{"detail":"Not authenticated"}` o `401 Unauthorized`

**Causa**: No se está enviando el token o el token es inválido/expirado.

**Solución**:
1. Obtener un nuevo token con `/auth/login`
2. Incluir el token en el header `Authorization: Bearer <token>`
3. Verificar que el token no haya expirado (por defecto expira en 30 minutos)

### Error 3: `{"detail":"Token inválido o expirado"}`

**Causa**: El token JWT ha expirado o es inválido.

**Solución**:
1. Hacer login nuevamente para obtener un nuevo token
2. Verificar que el token se esté enviando correctamente en el header

### Error 4: `{"detail":"Usuario inactivo"}`

**Causa**: El usuario está marcado como inactivo en la base de datos.

**Solución**: Activar el usuario en la base de datos o contactar al administrador.

---

## 🔧 Configuración del Frontend

### Actualizar el servicio API para incluir el token:

**En `frontend-citasmedicas/src/services/api.ts`:**

```typescript
import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URL || '/api'

// Obtener token del localStorage o sessionStorage
const getToken = () => {
  return localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
}

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para agregar el token a todas las peticiones
api.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para manejar errores 401 (no autenticado)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido - redirigir a login
      localStorage.removeItem('access_token')
      sessionStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
```

---

## 📝 Endpoints que Requieren Autenticación

### ✅ Endpoints Protegidos (requieren token):

- **Empleados**: Todos los endpoints (`GET`, `POST`, `PUT`, `DELETE`)
- **Asistencia**: Todos los endpoints (`GET`, `POST`, `PUT`, `DELETE`)
- **Citas**: Verificar si también necesitan autenticación
- **Pacientes**: Verificar si también necesitan autenticación
- **Médicos**: Verificar si también necesitan autenticación

### 🔓 Endpoints Públicos (no requieren token):

- `GET /` - Información de la API
- `GET /health` - Health check
- `POST /auth/login` - Login
- `POST /auth/register` - Registro (si está habilitado)
- `GET /docs` - Documentación Swagger (solo desarrollo)

---

## 🧪 Pruebas de Autenticación

### Prueba 1: Sin Token (debe fallar)
```bash
curl http://localhost:8000/empleados
```
**Resultado esperado**: `401 Unauthorized`

### Prueba 2: Con Token Válido (debe funcionar)
```bash
# 1. Obtener token
TOKEN=$(curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# 2. Usar token
curl http://localhost:8000/empleados \
  -H "Authorization: Bearer $TOKEN"
```
**Resultado esperado**: Lista de empleados o `[]` si está vacío

### Prueba 3: Con Token Inválido (debe fallar)
```bash
curl http://localhost:8000/empleados \
  -H "Authorization: Bearer token_invalido"
```
**Resultado esperado**: `401 Unauthorized` con mensaje "Token inválido o expirado"

---

## 🔑 Credenciales por Defecto

El sistema crea un usuario administrador por defecto:

- **Username**: `admin`
- **Password**: `admin123` (cambiar en producción)
- **Rol**: `admin`

**⚠️ IMPORTANTE**: Cambiar estas credenciales en producción.

---

## 📚 Recursos Adicionales

- Documentación de FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- Documentación de JWT: https://jwt.io/
- Archivo de autenticación: `auth.py`
- Router de autenticación: `routers/auth_router.py`

---

## ✅ Checklist de Seguridad

- [x] Autenticación JWT implementada
- [x] Sanitización de inputs
- [x] Validación de datos
- [x] Protección SQL Injection
- [x] Rate Limiting
- [x] Security Headers
- [x] CORS configurado
- [ ] Autorización por roles (opcional, para futuras mejoras)
- [ ] Logging de accesos (ya implementado)
- [ ] Expiración de tokens configurada (30 minutos por defecto)

---

## 🎯 Próximos Pasos Recomendados

1. **Implementar autorización por roles** - Restringir ciertos endpoints a roles específicos
2. **Refresh Tokens** - Implementar renovación automática de tokens
3. **Auditoría** - Registrar quién accede a qué endpoints
4. **Cambiar credenciales por defecto** - En producción, cambiar usuario admin
5. **HTTPS** - Usar HTTPS en producción para proteger tokens en tránsito

