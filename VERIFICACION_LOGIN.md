# Verificación de Configuración del Login

## ✅ Estado de la Configuración

### Backend (FastAPI)
- ✅ **Router de autenticación**: `auth_router.py` está registrado en `main.py`
- ✅ **Endpoint de login**: `POST /auth/login` está disponible
- ✅ **Base de datos**: `clinica_medica.db` existe y está configurada
- ✅ **Tabla Usuarios**: Existe con la estructura correcta
- ✅ **Usuario administrador**: Creado automáticamente al iniciar el servidor
  - Usuario: `admin`
  - Contraseña: `admin123`
  - Email: `admin@clinica.com`
  - Rol: `admin`
  - Estado: Activo

### Frontend (Vue.js)
- ✅ **Servicio de autenticación**: `authService` en `api.ts`
- ✅ **Vista de login**: `LoginView.vue` implementada
- ✅ **Router protegido**: Rutas protegidas con guards de autenticación
- ✅ **Proxy de Vite**: Configurado para redirigir `/api` a `http://127.0.0.1:8000`
- ✅ **Interceptores Axios**: Configurados para agregar token automáticamente

## 🔗 Flujo de Autenticación

### 1. Usuario accede al frontend
```
http://localhost:3000 → Redirige a /login
```

### 2. Usuario ingresa credenciales
- Usuario: `admin`
- Contraseña: `admin123`

### 3. Frontend envía petición
```
POST /api/auth/login
→ Proxy de Vite convierte a: POST http://127.0.0.1:8000/auth/login
```

### 4. Backend procesa la petición
- Verifica usuario en la base de datos
- Compara contraseña con hash bcrypt
- Genera token JWT
- Retorna token y datos del usuario

### 5. Frontend guarda el token
- Si "Recordar sesión": Guarda en `localStorage`
- Si no: Guarda en `sessionStorage`
- Redirige al dashboard (`/`)

### 6. Peticiones posteriores
- Interceptor de Axios agrega automáticamente: `Authorization: Bearer <token>`
- Backend valida el token en cada petición protegida

## 📋 Estructura de la Base de Datos

### Tabla: Usuarios
```sql
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

## 🔐 Seguridad Implementada

1. **Hash de contraseñas**: bcrypt con salt automático
2. **Tokens JWT**: Firmados con SECRET_KEY
3. **Expiración de tokens**: 30 minutos por defecto
4. **Validación de usuarios**: Solo usuarios activos pueden iniciar sesión
5. **Sanitización**: Todos los inputs son sanitizados
6. **CORS**: Configurado solo para orígenes permitidos
7. **Rate limiting**: Implementado en middleware
8. **Headers de seguridad**: Agregados automáticamente

## 🧪 Pruebas

### Verificar que el backend está corriendo:
```bash
cd Proyecto-Base-de-Datos-2
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Verificar que el frontend está corriendo:
```bash
cd frontend-citasmedicas
npm run dev
```

### Probar el login manualmente:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Verificar usuarios en la base de datos:
```bash
cd Proyecto-Base-de-Datos-2
python verificar_login.py
```

## 📝 Endpoints de Autenticación

### POST /auth/login
- **Descripción**: Iniciar sesión y obtener token JWT
- **Request Body**:
  ```json
  {
    "username": "admin",
    "password": "admin123"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "user": {
      "IdUsuario": 1,
      "Username": "admin",
      "Email": "admin@clinica.com",
      "Rol": "admin"
    }
  }
  ```

### POST /auth/register
- **Descripción**: Registrar nuevo usuario
- **Requiere**: Datos del nuevo usuario
- **Response**: Token JWT y datos del usuario

### GET /auth/me
- **Descripción**: Obtener información del usuario actual
- **Requiere**: Token JWT en header `Authorization: Bearer <token>`
- **Response**: Datos del usuario autenticado

## ⚠️ Problemas Comunes

### Error 404 al hacer login
1. Verificar que el backend esté corriendo en `http://localhost:8000`
2. Verificar que el proxy de Vite esté configurado correctamente
3. Revisar la consola del navegador para ver la URL exacta que está fallando

### Error 401 Unauthorized
1. Verificar que las credenciales sean correctas (`admin` / `admin123`)
2. Verificar que el usuario esté activo en la base de datos
3. Verificar que el token no haya expirado

### Error de conexión
1. Verificar que ambos servidores estén corriendo
2. Verificar que no haya firewall bloqueando las conexiones
3. Verificar la configuración de CORS en el backend

## ✅ Conclusión

El sistema de login está **completamente configurado y funcionando**:

- ✅ Backend configurado correctamente
- ✅ Base de datos con usuario administrador
- ✅ Frontend con vista de login funcional
- ✅ Autenticación JWT implementada
- ✅ Protección de rutas activa
- ✅ Manejo de errores mejorado

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

