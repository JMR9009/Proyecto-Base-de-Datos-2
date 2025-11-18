# 🔐 Cómo se Ejecuta la Autenticación en los Endpoints

## 📋 Flujo Completo de Autenticación

### 1. **Cliente (Frontend) hace una petición**

```typescript
// Frontend envía petición con token automáticamente
asistenciaService.getAll()
// → GET /api/asistencia
// → Header: Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2. **Interceptor de Axios agrega el token**

**Archivo:** `frontend-citasmedicas/src/services/api.ts` (líneas 18-30)

```typescript
api.interceptors.request.use(
  (config) => {
    const token = getToken() // Obtiene token de localStorage/sessionStorage
    if (token) {
      config.headers.Authorization = `Bearer ${token}` // Agrega token al header
    }
    return config
  }
)
```

### 3. **Backend recibe la petición**

FastAPI recibe la petición HTTP con el header `Authorization: Bearer <token>`

### 4. **Dependency `get_current_active_user` se ejecuta**

**Archivo:** `Proyecto-Base-de-Datos-2/auth.py` (líneas 167-176)

```python
async def get_current_active_user(
    current_user: dict = Depends(get_current_user)  # ← Se ejecuta primero
) -> dict:
    """Obtener usuario activo actual"""
    if not current_user.get("Activo"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    return current_user
```

### 5. **Dependency `get_current_user` extrae y valida el token**

**Archivo:** `Proyecto-Base-de-Datos-2/auth.py` (líneas 124-164)

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)  # ← Extrae token del header
) -> dict:
    """Obtener usuario actual desde el token JWT"""
    
    # Paso 1: Extraer token del header Authorization
    token = credentials.credentials  # "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    
    # Paso 2: Verificar y decodificar el token
    payload = verify_token(token)  # ← Llama a verify_token()
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    
    # Paso 3: Obtener ID de usuario del payload
    user_id_str = payload.get("sub")  # "1"
    user_id = int(user_id_str)  # 1
    
    # Paso 4: Buscar usuario en la base de datos
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo"
        )
    
    # Paso 5: Retornar datos del usuario
    return user  # {"IdUsuario": 1, "Username": "admin", "Email": "...", "Rol": "admin", "Activo": 1}
```

### 6. **Función `verify_token` valida el token JWT**

**Archivo:** `Proyecto-Base-de-Datos-2/auth.py` (líneas 57-64)

```python
def verify_token(token: str) -> Optional[dict]:
    """Verificar y decodificar token JWT"""
    try:
        # Decodificar token usando SECRET_KEY
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Retorna: {"sub": "1", "exp": 1234567890}
        return payload
    except JWTError as e:
        # Token inválido, expirado, o mal formado
        logger.warning(f"Error al verificar token: {str(e)}")
        return None
```

### 7. **Endpoint ejecuta con el usuario autenticado**

**Archivo:** `Proyecto-Base-de-Datos-2/routers/asistencia_router.py` (línea 41)

```python
@router.get("/", response_model=List[AsistenciaResponse])
def obtener_asistencias(current_user: dict = Depends(get_current_active_user)):
    # ↑ current_user contiene los datos del usuario autenticado
    # Ejemplo: {"IdUsuario": 1, "Username": "admin", "Rol": "admin", ...}
    
    # El endpoint puede usar current_user para:
    # - Registrar quién hizo la acción
    # - Filtrar datos según el rol
    # - Verificar permisos adicionales
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Asistencia ORDER BY Fecha DESC")
    # ... resto del código
```

## 🔄 Flujo Visual Completo

```
┌─────────────────────────────────────────────────────────────┐
│ 1. FRONTEND                                                 │
│    asistenciaService.getAll()                               │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. INTERCEPTOR AXIOS                                        │
│    Agrega: Authorization: Bearer <token>                   │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. BACKEND FASTAPI                                          │
│    Recibe: GET /asistencia                                  │
│    Header: Authorization: Bearer <token>                   │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. DEPENDENCY: get_current_active_user                      │
│    ↓                                                         │
│ 5. DEPENDENCY: get_current_user                             │
│    ↓                                                         │
│ 6. HTTPBearer extrae token del header                        │
│    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."        │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. verify_token(token)                                      │
│    ↓                                                         │
│    jwt.decode(token, SECRET_KEY, algorithms=[HS256])        │
│    ↓                                                         │
│    Retorna: {"sub": "1", "exp": 1234567890}                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. get_user_by_id(user_id)                                  │
│    SELECT * FROM Usuarios WHERE IdUsuario = 1               │
│    ↓                                                         │
│    Retorna: {"IdUsuario": 1, "Username": "admin", ...}      │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 9. Verificar que usuario esté activo                         │
│    if not current_user.get("Activo"):                        │
│        raise HTTPException(403)                              │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 10. ENDPOINT EJECUTA                                         │
│     def obtener_asistencias(current_user: dict):             │
│         # current_user disponible aquí                        │
│         # Puede usar: current_user["IdUsuario"]              │
│         # Puede usar: current_user["Rol"]                    │
│         return asistencias                                   │
└─────────────────────────────────────────────────────────────┘
```

## 📝 Ejemplo Práctico: Endpoint Protegido

### Backend (`routers/asistencia_router.py`)

```python
from auth import get_current_active_user
from fastapi import Depends

@router.get("/", response_model=List[AsistenciaResponse])
def obtener_asistencias(current_user: dict = Depends(get_current_active_user)):
    # ↑ Esta línea hace que FastAPI ejecute get_current_active_user ANTES
    #   de ejecutar el código de esta función
    
    # Si el token es inválido o el usuario no existe:
    # → Se lanza HTTPException(401) y esta función NUNCA se ejecuta
    
    # Si todo está bien:
    # → current_user contiene los datos del usuario autenticado
    # → Esta función se ejecuta normalmente
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Asistencia ORDER BY Fecha DESC")
    # ... resto del código
```

### Frontend (`services/api.ts`)

```typescript
// El interceptor agrega automáticamente el token
export const asistenciaService = {
  getAll: () => api.get<Asistencia[]>('/asistencia')
  // ↑ Esto se convierte en:
  // GET /api/asistencia
  // Headers: {
  //   Authorization: "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  // }
}
```

## 🔍 Verificación Paso a Paso

### Paso 1: Token en el Header

Cuando el frontend hace una petición, el interceptor agrega:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzM0NTY3ODkwfQ.signature
```

### Paso 2: FastAPI Extrae el Token

```python
# En auth.py, línea 124-128
security = HTTPBearer()  # ← Define el esquema de seguridad

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
    # ↑ FastAPI automáticamente extrae el token del header Authorization
):
    token = credentials.credentials  # ← Token extraído
```

### Paso 3: Validación del Token

```python
# En auth.py, línea 57-64
def verify_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    # ↑ Verifica:
    # - Que el token esté firmado con SECRET_KEY
    # - Que no haya expirado (verifica campo "exp")
    # - Que el formato sea correcto
```

### Paso 4: Obtener Usuario de la BD

```python
# En auth.py, línea 96-121
def get_user_by_id(user_id: int):
    cursor.execute(
        "SELECT IdUsuario, Username, Email, Rol, Activo FROM Usuarios WHERE IdUsuario = ?",
        (user_id,)
    )
    # ↑ Busca el usuario en la base de datos
```

### Paso 5: Verificar Usuario Activo

```python
# En auth.py, línea 167-176
async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if not current_user.get("Activo"):
        raise HTTPException(403, "Usuario inactivo")
    return current_user
```

### Paso 6: Endpoint Ejecuta

```python
# En routers/asistencia_router.py
@router.get("/")
def obtener_asistencias(current_user: dict = Depends(get_current_active_user)):
    # ↑ Si llegamos aquí, significa que:
    # ✅ Token válido
    # ✅ Usuario existe
    # ✅ Usuario está activo
    # ✅ current_user contiene los datos del usuario
    
    # Ahora puedes usar current_user en tu lógica
    logger.info(f"Usuario {current_user['Username']} consultó asistencias")
    # ... resto del código
```

## ⚠️ Qué Pasa si Falla la Autenticación

### Caso 1: No hay token
```
Frontend → GET /asistencia (sin header Authorization)
Backend → HTTPException(401, "Not authenticated")
Frontend → Interceptor detecta 401 → Redirige a /login
```

### Caso 2: Token inválido
```
Frontend → GET /asistencia (token mal formado)
Backend → verify_token() retorna None
Backend → HTTPException(401, "Token inválido o expirado")
Frontend → Interceptor detecta 401 → Redirige a /login
```

### Caso 3: Token expirado
```
Frontend → GET /asistencia (token expirado)
Backend → jwt.decode() lanza JWTError (expired)
Backend → verify_token() retorna None
Backend → HTTPException(401, "Token inválido o expirado")
Frontend → Interceptor detecta 401 → Redirige a /login
```

### Caso 4: Usuario inactivo
```
Frontend → GET /asistencia (token válido)
Backend → get_user_by_id() encuentra usuario
Backend → get_current_active_user() verifica Activo = 0
Backend → HTTPException(403, "Usuario inactivo")
Frontend → Muestra error 403
```

## 🎯 Resumen

1. **Frontend** agrega token automáticamente (interceptor Axios)
2. **Backend** recibe petición con header `Authorization: Bearer <token>`
3. **FastAPI** ejecuta `Depends(get_current_active_user)` ANTES del endpoint
4. **get_current_active_user** ejecuta `Depends(get_current_user)`
5. **get_current_user** extrae token con `HTTPBearer`
6. **verify_token** valida y decodifica el token JWT
7. **get_user_by_id** busca usuario en la base de datos
8. **get_current_active_user** verifica que usuario esté activo
9. **Endpoint** se ejecuta con `current_user` disponible
10. Si algo falla, se lanza `HTTPException(401)` y el endpoint NO se ejecuta

## 📚 Archivos Clave

- `auth.py` - Funciones de autenticación JWT
- `routers/*_router.py` - Endpoints protegidos con `Depends(get_current_active_user)`
- `frontend-citasmedicas/src/services/api.ts` - Interceptores Axios

