# 🔐 Ejemplo Práctico: Cómo se Ejecuta la Autenticación

## 📝 Ejemplo Completo Paso a Paso

### Ejemplo: Endpoint `GET /asistencia`

#### 1. Frontend hace la petición

```typescript
// frontend-citasmedicas/src/views/AsistenciaView.vue (línea 780)
const response = await asistenciaService.getAll()
```

#### 2. Servicio API envía la petición

```typescript
// frontend-citasmedicas/src/services/api.ts (línea 278)
export const asistenciaService = {
  getAll: () => api.get<Asistencia[]>('/asistencia')
}
```

#### 3. Interceptor agrega el token automáticamente

```typescript
// frontend-citasmedicas/src/services/api.ts (líneas 18-30)
api.interceptors.request.use((config) => {
  const token = getToken() // Obtiene de localStorage: "eyJhbGciOiJIUzI1NiIs..."
  if (token) {
    config.headers.Authorization = `Bearer ${token}` // Agrega al header
  }
  return config
})
```

**Petición HTTP enviada:**
```
GET /api/asistencia HTTP/1.1
Host: localhost:3000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzM0NTY3ODkwfQ.signature
Content-Type: application/json
```

#### 4. Proxy de Vite redirige al backend

```
GET /api/asistencia → Proxy → GET http://127.0.0.1:8000/asistencia
```

#### 5. Backend recibe la petición

FastAPI recibe la petición y ve que el endpoint tiene `Depends(get_current_active_user)`

```python
# routers/asistencia_router.py (línea 197)
@router.get("/", response_model=List[AsistenciaResponse])
def obtener_asistencias(current_user: dict = Depends(get_current_active_user)):
    # ↑ FastAPI ve este Depends() y ejecuta get_current_active_user ANTES
```

#### 6. FastAPI ejecuta `get_current_active_user`

```python
# auth.py (línea 168)
async def get_current_active_user(
    current_user: dict = Depends(get_current_user)  # ← Ejecuta get_current_user primero
) -> dict:
```

#### 7. FastAPI ejecuta `get_current_user`

```python
# auth.py (línea 125)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
    # ↑ HTTPBearer extrae automáticamente el token del header Authorization
) -> dict:
    token = credentials.credentials  # "eyJhbGciOiJIUzI1NiIs..."
```

#### 8. Se valida el token

```python
# auth.py (línea 131)
payload = verify_token(token)  # Llama a verify_token()

# auth.py (línea 57-64)
def verify_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    # Retorna: {"sub": "1", "exp": 1734567890}
    return payload
```

#### 9. Se obtiene el usuario de la BD

```python
# auth.py (línea 139-149)
user_id_str = payload.get("sub")  # "1"
user_id = int(user_id_str)  # 1

# auth.py (línea 157)
user = get_user_by_id(user_id)  # Busca en la BD

# auth.py (línea 96-121)
def get_user_by_id(user_id: int):
    cursor.execute(
        "SELECT IdUsuario, Username, Email, Rol, Activo FROM Usuarios WHERE IdUsuario = ?",
        (user_id,)
    )
    # Retorna: {"IdUsuario": 1, "Username": "admin", "Email": "admin@clinica.com", "Rol": "admin", "Activo": 1}
```

#### 10. Se verifica que el usuario esté activo

```python
# auth.py (línea 172)
if not current_user.get("Activo"):  # Verifica que Activo = 1
    raise HTTPException(403, "Usuario inactivo")
return current_user  # Retorna usuario activo
```

#### 11. El endpoint se ejecuta

```python
# routers/asistencia_router.py (línea 197)
@router.get("/")
def obtener_asistencias(current_user: dict = Depends(get_current_active_user)):
    # ↑ Si llegamos aquí, significa que:
    # ✅ Token válido
    # ✅ Usuario existe en BD
    # ✅ Usuario está activo
    # ✅ current_user = {"IdUsuario": 1, "Username": "admin", "Rol": "admin", ...}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Asistencia ORDER BY Fecha DESC")
    # ... resto del código
    return asistencias
```

## 🔍 Código Real de los Archivos

### Archivo: `auth.py`

```python
# Línea 25: Define el esquema de seguridad HTTP Bearer
security = HTTPBearer()

# Línea 125-165: Extrae y valida el token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    token = credentials.credentials  # Extrae token del header
    payload = verify_token(token)    # Valida token
    user_id = int(payload.get("sub")) # Obtiene ID de usuario
    user = get_user_by_id(user_id)   # Busca en BD
    return user

# Línea 168-177: Verifica que usuario esté activo
async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    if not current_user.get("Activo"):
        raise HTTPException(403, "Usuario inactivo")
    return current_user
```

### Archivo: `routers/asistencia_router.py`

```python
# Línea 1: Importa la función de autenticación
from auth import get_current_active_user

# Línea 197: Usa Depends() para proteger el endpoint
@router.get("/", response_model=List[AsistenciaResponse])
def obtener_asistencias(current_user: dict = Depends(get_current_active_user)):
    # current_user está disponible aquí con los datos del usuario autenticado
    conn = get_db_connection()
    # ... código del endpoint
```

### Archivo: `frontend-citasmedicas/src/services/api.ts`

```typescript
// Línea 18-30: Interceptor que agrega token automáticamente
api.interceptors.request.use((config) => {
  const token = getToken() // Obtiene token de localStorage/sessionStorage
  if (token) {
    config.headers.Authorization = `Bearer ${token}` // Agrega al header
  }
  return config
})
```

## ⚡ Orden de Ejecución

```
1. Frontend: asistenciaService.getAll()
   ↓
2. Interceptor: Agrega Authorization: Bearer <token>
   ↓
3. Backend: Recibe GET /asistencia con header Authorization
   ↓
4. FastAPI: Detecta Depends(get_current_active_user)
   ↓
5. Ejecuta: get_current_active_user()
   ↓
6. Ejecuta: get_current_user() (dependency)
   ↓
7. Ejecuta: HTTPBearer (extrae token del header)
   ↓
8. Ejecuta: verify_token(token)
   ↓
9. Ejecuta: jwt.decode() (valida token)
   ↓
10. Ejecuta: get_user_by_id() (busca en BD)
   ↓
11. Verifica: Usuario activo
   ↓
12. Retorna: current_user al endpoint
   ↓
13. Ejecuta: obtener_asistencias(current_user)
   ↓
14. Retorna: Lista de asistencias al frontend
```

## 🎯 Puntos Clave

1. **`Depends()`** hace que FastAPI ejecute la función ANTES del endpoint
2. **`HTTPBearer()`** extrae automáticamente el token del header `Authorization`
3. **`verify_token()`** valida que el token sea válido y no haya expirado
4. **`get_user_by_id()`** busca el usuario en la base de datos
5. Si cualquier paso falla, se lanza `HTTPException(401)` y el endpoint NO se ejecuta
6. Solo si TODO pasa, el endpoint recibe `current_user` y se ejecuta

## 📚 Resumen

La autenticación se ejecuta **automáticamente** cuando usas `Depends(get_current_active_user)` en un endpoint. FastAPI ejecuta toda la cadena de validación antes de permitir que el código del endpoint se ejecute.

