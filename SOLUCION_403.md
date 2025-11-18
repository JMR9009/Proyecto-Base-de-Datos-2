# 🔧 Solución al Error 403 (Forbidden)

## ❌ Error Original
```
GET http://127.0.0.1:8000/empleados/ 403 (Forbidden)
```

## 🔍 Causas Posibles

El error 403 puede ocurrir por varias razones:

1. **Token no enviado**: El token JWT no se está enviando en el header `Authorization`
2. **Token inválido**: El token ha expirado o es inválido
3. **Usuario no autenticado**: No se ha iniciado sesión correctamente
4. **Usuario inactivo**: El usuario está marcado como inactivo en la base de datos
5. **Token no guardado**: El token no se guardó correctamente después del login

## ✅ Soluciones Aplicadas

### 1. Mejorado Manejo de Errores 403 en Frontend
Se actualizó el interceptor de axios para manejar tanto errores 401 como 403:
- Si no hay token → Redirigir a login
- Si hay token pero es inválido → Limpiar almacenamiento y redirigir a login
- Si el usuario está inactivo → Limpiar y redirigir a login

### 2. Verificación de Autenticación
El router ya tiene protección con `meta: { requiresAuth: true }` que verifica el token antes de acceder a las rutas.

## 🔄 Pasos para Resolver el Problema

### Paso 1: Verificar que estás autenticado

1. Abre las DevTools del navegador (F12)
2. Ve a la pestaña **Application** (o **Almacenamiento**)
3. Busca en **Local Storage** o **Session Storage**:
   - Debe existir `access_token` con un valor (el token JWT)
   - Debe existir `user` con información del usuario

### Paso 2: Verificar el Login

1. Ve a `http://localhost:3001/login`
2. Inicia sesión con:
   - Usuario: `admin`
   - Contraseña: `admin123`
3. Verifica que después del login se guarden los tokens

### Paso 3: Verificar que el Token se Envíe

1. Abre las DevTools (F12)
2. Ve a la pestaña **Network** (Red)
3. Intenta acceder a `/empleados`
4. Haz clic en la petición `empleados`
5. Ve a la pestaña **Headers**
6. Busca el header `Authorization`:
   - Debe decir: `Authorization: Bearer <tu-token-aqui>`
   - Si no aparece, el token no se está enviando

### Paso 4: Verificar el Token en el Backend

Si el token se está enviando pero aún recibes 403:

1. Verifica que el usuario `admin` esté activo en la base de datos:
   ```bash
   cd Proyecto-Base-de-Datos-2
   python -c "from database import get_db_connection; conn = get_db_connection(); cursor = conn.cursor(); cursor.execute('SELECT Username, Activo FROM Usuarios WHERE Username = \"admin\"'); print(cursor.fetchone())"
   ```
   - Debe mostrar `Activo = 1`

2. Verifica que el token sea válido:
   - Copia el token del Local Storage
   - Ve a `http://127.0.0.1:8000/docs`
   - Haz clic en "Authorize"
   - Pega el token (sin "Bearer ")
   - Intenta hacer una petición GET a `/empleados`

## 🐛 Debugging Adicional

### Verificar en la Consola del Navegador

Abre la consola (F12 → Console) y ejecuta:

```javascript
// Verificar si hay token
console.log('Token:', localStorage.getItem('access_token') || sessionStorage.getItem('access_token'))

// Verificar usuario
console.log('User:', localStorage.getItem('user') || sessionStorage.getItem('user'))

// Probar petición manual
fetch('http://localhost:3001/api/empleados', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
})
.then(r => r.json())
.then(console.log)
.catch(console.error)
```

### Verificar en el Backend

Revisa los logs del servidor backend. Deberías ver:
- Si la petición llega con el header `Authorization`
- Si el token se valida correctamente
- Si hay algún error al obtener el usuario

## ⚠️ Soluciones Comunes

### Si no hay token:
1. Haz login nuevamente
2. Verifica que el login sea exitoso (debe redirigir a `/`)
3. Verifica que el token se guarde en Local/Session Storage

### Si el token es inválido:
1. Haz logout y login nuevamente
2. Verifica que el token no haya expirado (duración: 1 mes)
3. Verifica que el `SECRET_KEY` en el backend no haya cambiado

### Si el usuario está inactivo:
1. Verifica en la base de datos que `Activo = 1` para el usuario
2. Si está inactivo, actívalo:
   ```sql
   UPDATE Usuarios SET Activo = 1 WHERE Username = 'admin';
   ```

## 📝 Notas Importantes

- El token se envía automáticamente en todas las peticiones gracias al interceptor de axios
- Si recibes 403, el interceptor ahora redirige automáticamente a `/login`
- El token tiene una duración de 1 mes (43,200 minutos)
- Todos los endpoints requieren autenticación excepto `/auth/login` y `/auth/register`

