# 🔐 Implementación JWT - Completada

## ✅ Estado: IMPLEMENTADO Y FUNCIONANDO

## 📁 Archivos Creados

### 1. `auth.py` - Funciones de Autenticación JWT
**Ubicación**: `Proyecto-Base-de-Datos-2/auth.py`

**Funciones implementadas**:
- ✅ `verify_password()` - Verificar contraseña contra hash
- ✅ `get_password_hash()` - Generar hash de contraseña (bcrypt)
- ✅ `create_access_token()` - Crear token JWT
- ✅ `verify_token()` - Verificar y decodificar token JWT
- ✅ `get_user_by_username()` - Obtener usuario por username
- ✅ `get_user_by_id()` - Obtener usuario por ID
- ✅ `get_current_user()` - Dependency para obtener usuario del token
- ✅ `get_current_active_user()` - Dependency para usuario activo
- ✅ `require_role()` - Dependency para requerir rol específico

### 2. `routers/auth_router.py` - Endpoints de Autenticación
**Ubicación**: `Proyecto-Base-de-Datos-2/routers/auth_router.py`

**Endpoints implementados**:
- ✅ `POST /auth/login` - Login y obtener token
- ✅ `POST /auth/register` - Registro de nuevo usuario
- ✅ `GET /auth/me` - Obtener información del usuario actual

### 3. `init_admin.py` - Inicialización de Usuario Admin
**Ubicación**: `Proyecto-Base-de-Datos-2/init_admin.py`

**Funcionalidad**:
- ✅ Crea usuario administrador por defecto
- ✅ Usuario: `admin`
- ✅ Contraseña: `admin123`
- ✅ Email: `admin@clinica.com`
- ✅ Rol: `admin`

### 4. `database.py` - Actualizado
**Cambios**:
- ✅ Tabla `Usuarios` creada automáticamente
- ✅ Campos: IdUsuario, Username, PasswordHash, Email, Rol, Activo, CreatedAt

### 5. `requirements.txt` - Actualizado
**Dependencias agregadas**:
- ✅ `python-jose[cryptography]==3.3.0` - Para JWT
- ✅ `passlib[bcrypt]==1.7.4` - Para hash de contraseñas

### 6. `main.py` - Actualizado
**Cambios**:
- ✅ Import de `auth_router`
- ✅ Router de autenticación incluido
- ✅ Inicialización de usuario admin

---

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` o configura estas variables:

```env
# JWT Configuration
SECRET_KEY=tu-clave-secreta-super-segura-cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development  # o production
```

**⚠️ IMPORTANTE**: Cambia `SECRET_KEY` en producción por una clave segura y aleatoria.

---

## 📖 Uso de la API

### 1. Login (Obtener Token)

**Endpoint**: `POST /auth/login`

**Request**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "IdUsuario": 1,
    "Username": "admin",
    "Email": "admin@clinica.com",
    "Rol": "admin"
  }
}
```

### 2. Registro (Crear Usuario)

**Endpoint**: `POST /auth/register`

**Request**:
```json
{
  "username": "nuevo_usuario",
  "password": "password123",
  "email": "usuario@example.com",
  "rol": "usuario"
}
```

**Response**: Similar al login, retorna token automáticamente.

### 3. Obtener Usuario Actual

**Endpoint**: `GET /auth/me`

**Headers**:
```
Authorization: Bearer <token>
```

**Response**:
```json
{
  "IdUsuario": 1,
  "Username": "admin",
  "Email": "admin@clinica.com",
  "Rol": "admin"
}
```

---

## 🔒 Proteger Endpoints

### Opción 1: Proteger con Usuario Autenticado

```python
from fastapi import Depends
from auth import get_current_active_user

@app.get("/medicos")
def obtener_medicos(current_user: dict = Depends(get_current_active_user)):
    # Solo usuarios autenticados pueden acceder
    ...
```

### Opción 2: Proteger con Rol Específico

```python
from auth import require_role

@app.delete("/medicos/{id}")
def eliminar_medico(
    id: int,
    current_user: dict = Depends(require_role("admin"))
):
    # Solo usuarios con rol "admin" pueden acceder
    ...
```

---

## 🧪 Pruebas

### Instalar Dependencias

```bash
cd Proyecto-Base-de-Datos-2
pip install -r requirements.txt
```

### Iniciar Servidor

```bash
python -m uvicorn main:app --reload --port 8000
```

### Probar Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Probar Endpoint Protegido

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer <token_obtenido_del_login>"
```

---

## 📊 Estructura de la Tabla Usuarios

```sql
CREATE TABLE Usuarios (
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

## ✅ Checklist de Implementación

- [x] Dependencias instaladas (`python-jose`, `passlib`)
- [x] `auth.py` creado con funciones JWT
- [x] `routers/auth_router.py` creado con endpoints
- [x] Tabla `Usuarios` creada en BD
- [x] Usuario administrador inicializado
- [x] `requirements.txt` actualizado
- [x] `main.py` actualizado con router
- [x] Documentación completa

---

## 🎯 Resumen

**JWT Authentication**: ✅ **100% IMPLEMENTADO**

- ✅ Login y registro funcionando
- ✅ Tokens JWT generados y verificados
- ✅ Protección de endpoints disponible
- ✅ Usuario administrador creado automáticamente
- ✅ Hash de contraseñas con bcrypt
- ✅ Sistema de roles implementado

**Rate Limiting**: ✅ **YA ESTABA IMPLEMENTADO**

- ✅ 100 requests por 60 segundos por IP
- ✅ Headers informativos
- ✅ Respuesta 429 cuando se excede

---

## 🔐 Seguridad Implementada

1. **Contraseñas**: Hash con bcrypt (no se almacenan en texto plano)
2. **Tokens**: Firmados con SECRET_KEY
3. **Expiración**: Tokens expiran después de 30 minutos (configurable)
4. **Validación**: Tokens verificados en cada request protegido
5. **Roles**: Sistema de roles para control de acceso
6. **Sanitización**: Inputs sanitizados antes de procesar

---

## 📝 Notas Importantes

1. **Cambiar SECRET_KEY en producción**: Usa una clave segura y aleatoria
2. **Cambiar contraseña del admin**: Después del primer login, cambia la contraseña
3. **HTTPS en producción**: Los tokens deben enviarse solo sobre HTTPS
4. **Refresh tokens**: Considera implementar refresh tokens para mejor UX

---

## 🚀 Próximos Pasos Opcionales

1. Implementar refresh tokens
2. Agregar endpoints de cambio de contraseña
3. Agregar endpoints de recuperación de contraseña
4. Implementar rate limiting por usuario (no solo por IP)
5. Agregar logging de intentos de login fallidos
6. Implementar bloqueo de cuenta después de X intentos fallidos

