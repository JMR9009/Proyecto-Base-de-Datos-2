# 📍 Ubicación de la Configuración JWT

## 🗂️ Archivos Principales de Autenticación JWT

### 1. **`auth.py`** - Módulo Principal de JWT
**Ubicación:** `Proyecto-Base-de-Datos-2/auth.py`

**Contiene:**
- ✅ Configuración de seguridad (SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES)
- ✅ Funciones de hash de contraseñas (bcrypt)
- ✅ `create_access_token()` - Crear token JWT
- ✅ `verify_token()` - Verificar y decodificar token JWT
- ✅ `get_current_user()` - Dependency para obtener usuario del token
- ✅ `get_current_active_user()` - Dependency para obtener usuario activo
- ✅ `require_role()` - Dependency para requerir roles específicos
- ✅ Funciones de consulta de usuarios (`get_user_by_username`, `get_user_by_id`)

**Configuración clave:**
```python
SECRET_KEY = os.getenv("SECRET_KEY", "tu-clave-secreta-super-segura-cambiar-en-produccion")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
```

---

### 2. **`routers/auth_router.py`** - Endpoints de Autenticación
**Ubicación:** `Proyecto-Base-de-Datos-2/routers/auth_router.py`

**Contiene:**
- ✅ `POST /auth/login` - Endpoint para iniciar sesión y obtener token
- ✅ `POST /auth/register` - Endpoint para registrar nuevos usuarios
- ✅ `GET /auth/me` - Endpoint para obtener información del usuario actual
- ✅ Modelos Pydantic (LoginRequest, RegisterRequest, TokenResponse, UserResponse)

**Endpoints:**
```python
@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest):
    # Verifica usuario y contraseña
    # Genera token JWT usando create_access_token()
    # Retorna token y datos del usuario

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    # Requiere token JWT válido
    # Retorna información del usuario autenticado
```

---

### 3. **`main.py`** - Registro del Router
**Ubicación:** `Proyecto-Base-de-Datos-2/main.py`

**Línea 6:** Importación del router
```python
from routers import cita_router, auth_router, asistencia_router, empleado_router
```

**Línea 63:** Registro del router en la aplicación
```python
app.include_router(auth_router.router)
```

---

### 4. **`database.py`** - Tabla de Usuarios
**Ubicación:** `Proyecto-Base-de-Datos-2/database.py`

**Líneas 59-70:** Creación de la tabla Usuarios
```python
CREATE TABLE IF NOT EXISTS Usuarios (
    IdUsuario INTEGER PRIMARY KEY AUTOINCREMENT,
    Username TEXT NOT NULL UNIQUE,
    PasswordHash TEXT NOT NULL,
    Email TEXT NOT NULL UNIQUE,
    Rol TEXT DEFAULT 'usuario',
    Activo INTEGER DEFAULT 1,
    CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP
)
```

---

### 5. **`init_admin.py`** - Usuario Administrador por Defecto
**Ubicación:** `Proyecto-Base-de-Datos-2/init_admin.py`

**Contiene:**
- ✅ Función `init_admin_user()` que crea el usuario administrador
- ✅ Usuario: `admin`
- ✅ Contraseña: `admin123`
- ✅ Se ejecuta automáticamente al iniciar el servidor (línea 58-59 de main.py)

---

## 🔐 Configuración de Seguridad

### Variables de Entorno (Opcional)
Puedes crear un archivo `.env` en `Proyecto-Base-de-Datos-2/`:

```env
SECRET_KEY=tu-clave-secreta-super-segura-cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development
```

**⚠️ IMPORTANTE:** En producción, cambia `SECRET_KEY` por una clave segura y aleatoria.

---

## 📋 Flujo de Autenticación

### 1. Login (Obtener Token)
```
Frontend → POST /api/auth/login
         → Backend: routers/auth_router.py → login()
         → auth.py: get_user_by_username()
         → auth.py: verify_password()
         → auth.py: create_access_token()
         → Retorna token JWT
```

### 2. Usar Token en Peticiones
```
Frontend → Agrega header: Authorization: Bearer <token>
         → Backend: auth.py → get_current_user()
         → auth.py: verify_token()
         → auth.py: get_user_by_id()
         → Retorna usuario autenticado
```

### 3. Proteger Endpoints
```python
from auth import get_current_active_user

@router.get("/empleados")
def obtener_empleados(current_user: dict = Depends(get_current_active_user)):
    # Solo usuarios autenticados pueden acceder
    # current_user contiene los datos del usuario
```

---

## 🔍 Dónde se Usa JWT

### Endpoints Protegidos (requieren token JWT):

1. **`routers/empleado_router.py`**
   - Todos los endpoints usan `Depends(get_current_active_user)`

2. **`routers/asistencia_router.py`**
   - Todos los endpoints usan `Depends(get_current_active_user)`

3. **`routers/auth_router.py`**
   - `GET /auth/me` usa `Depends(get_current_active_user)`

---

## 📦 Dependencias Necesarias

**Archivo:** `requirements.txt`

```txt
python-jose[cryptography]==3.3.0  # Para JWT
passlib[bcrypt]==1.7.4            # Para hash de contraseñas
```

---

## 🎯 Resumen de Ubicaciones

| Componente | Archivo | Líneas Clave |
|------------|---------|--------------|
| **Configuración JWT** | `auth.py` | 17-19 (SECRET_KEY, ALGORITHM) |
| **Crear Token** | `auth.py` | 38-54 (`create_access_token()`) |
| **Verificar Token** | `auth.py` | 57-64 (`verify_token()`) |
| **Obtener Usuario** | `auth.py` | 124-164 (`get_current_user()`) |
| **Endpoint Login** | `routers/auth_router.py` | 64-111 (`POST /auth/login`) |
| **Registro Router** | `main.py` | 63 (`app.include_router()`) |
| **Tabla Usuarios** | `database.py` | 59-70 (`CREATE TABLE Usuarios`) |
| **Usuario Admin** | `init_admin.py` | 7-30 (`init_admin_user()`) |

---

## ✅ Verificación

Para verificar que todo está configurado:

```bash
cd Proyecto-Base-de-Datos-2
python verificar_importaciones.py
```

Este script verifica que:
- ✅ Los routers se pueden importar
- ✅ Los prefijos están correctos
- ✅ Las rutas están disponibles
- ✅ `main.py` puede importar correctamente

---

---

## 🌐 Frontend - Configuración JWT

### 6. **`frontend-citasmedicas/src/services/api.ts`** - Cliente API
**Ubicación:** `frontend-citasmedicas/src/services/api.ts`

**Líneas 6-9:** Función para obtener token
```typescript
const getToken = (): string | null => {
  return localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
}
```

**Líneas 18-30:** Interceptor para agregar token automáticamente
```typescript
api.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  }
)
```

**Líneas 32-49:** Interceptor para manejar errores 401
```typescript
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Limpiar tokens y redirigir a login
    }
  }
)
```

**Líneas 797-806:** Servicio de autenticación
```typescript
export const authService = {
  login: (data: LoginRequest) => api.post<LoginResponse>('/auth/login', data),
  register: (data: RegisterRequest) => api.post<LoginResponse>('/auth/register', data),
  getCurrentUser: () => api.get('/auth/me'),
  logout: () => {
    localStorage.removeItem('access_token')
    sessionStorage.removeItem('access_token')
  }
}
```

---

### 7. **`frontend-citasmedicas/src/views/LoginView.vue`** - Vista de Login
**Ubicación:** `frontend-citasmedicas/src/views/LoginView.vue`

**Líneas 131-154:** Función de login
```typescript
const response = await authService.login({
  username: loginForm.username,
  password: loginForm.password
})

// Guardar token según preferencia del usuario
if (rememberMe.value) {
  localStorage.setItem('access_token', token)
} else {
  sessionStorage.setItem('access_token', token)
}
```

---

### 8. **`frontend-citasmedicas/src/router/index.ts`** - Protección de Rutas
**Ubicación:** `frontend-citasmedicas/src/router/index.ts`

**Líneas 4-17:** Guard de autenticación
```typescript
const isAuthenticated = (): boolean => {
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
  return !!token
}

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
  
  if (to.meta.requiresAuth !== false && !token && to.path !== '/login') {
    next('/login')
  }
  // ...
})
```

---

## 📚 Documentación Adicional

- `JWT_IMPLEMENTATION.md` - Documentación completa de JWT
- `VERIFICACION_LOGIN.md` - Verificación del sistema de login
- `SOLUCION_SEGURIDAD.md` - Solución de seguridad implementada

