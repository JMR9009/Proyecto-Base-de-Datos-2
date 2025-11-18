# ✅ Verificación de Conexión - Módulo de Asistencia

## 🔗 Estado de la Conexión

### Backend ✅
- ✅ Router registrado en `main.py` (línea 65)
- ✅ Tabla `Asistencia` creada en `database.py` (líneas 96-115)
- ✅ Modelo `Asistencia` en `models/asistencia.py`
- ✅ Endpoints disponibles en `routers/asistencia_router.py`
- ✅ Autenticación JWT requerida en todos los endpoints

### Frontend ✅
- ✅ Servicio `asistenciaService` configurado en `api.ts` (líneas 277-288)
- ✅ Vista `AsistenciaView.vue` usando el servicio
- ✅ Interceptores Axios configurados para agregar token automáticamente

## 📋 Endpoints Disponibles

| Método | Ruta | Descripción | Frontend |
|--------|------|-------------|----------|
| POST | `/asistencia/` | Crear registro | `asistenciaService.create()` |
| POST | `/asistencia/entrada` | Registrar entrada | `asistenciaService.registrarEntrada()` |
| PUT | `/asistencia/{id}/salida` | Registrar salida | `asistenciaService.registrarSalida()` |
| GET | `/asistencia/` | Obtener todos | `asistenciaService.getAll()` |
| GET | `/asistencia/{id}` | Obtener por ID | `asistenciaService.getById()` |
| GET | `/asistencia/empleado/{id}` | Por empleado | `asistenciaService.getByEmpleado()` |
| GET | `/asistencia/fecha/{fecha}` | Por fecha | `asistenciaService.getByFecha()` |
| GET | `/asistencia/rango` | Por rango | `asistenciaService.getByRangoFechas()` |
| PUT | `/asistencia/{id}` | Actualizar | `asistenciaService.update()` |
| DELETE | `/asistencia/{id}` | Eliminar | `asistenciaService.delete()` |

## 🗄️ Estructura de la Base de Datos

```sql
CREATE TABLE IF NOT EXISTS Asistencia (
    IdAsistencia INTEGER PRIMARY KEY AUTOINCREMENT,
    IdEmpleado INTEGER NOT NULL,
    Fecha TEXT NOT NULL,
    HoraEntrada TEXT,
    HoraSalida TEXT,
    TipoRegistro TEXT NOT NULL,
    TipoRegistroOrigen TEXT DEFAULT 'manual',
    Estado TEXT DEFAULT 'presente',
    Observaciones TEXT,
    Justificacion TEXT,
    HorasTrabajadas REAL,
    Latitud REAL,
    Longitud REAL,
    CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (IdEmpleado) REFERENCES Empleados(IdEmpleado)
)
```

## 🔐 Seguridad

Todos los endpoints requieren autenticación JWT:
```python
current_user: dict = Depends(get_current_active_user)
```

El frontend agrega automáticamente el token en cada petición mediante interceptores Axios.

## ✅ Verificación Rápida

### 1. Verificar que el backend esté corriendo:
```bash
cd Proyecto-Base-de-Datos-2
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Verificar endpoints en Swagger:
```
http://localhost:8000/docs
```

Busca la sección "asistencia" y verifica que todos los endpoints aparezcan.

### 3. Probar desde el frontend:
1. Inicia sesión con `admin` / `admin123`
2. Ve a "Asistencia" en el menú
3. Intenta crear un registro de asistencia

## 🐛 Solución de Problemas

### Error 404 en endpoints de asistencia
- Verifica que el backend esté corriendo
- Verifica que el router esté registrado en `main.py`
- Reinicia el servidor backend

### Error 401 Unauthorized
- Verifica que hayas iniciado sesión
- Verifica que el token esté guardado en localStorage/sessionStorage
- Verifica que el interceptor de Axios esté agregando el token

### Error al crear registro
- Verifica que existan empleados en la base de datos
- Verifica que el formato de fecha sea YYYY-MM-DD
- Verifica que el formato de hora sea HH:mm

## 📝 Notas

- Todos los endpoints están protegidos con JWT
- La tabla `Asistencia` tiene relación con `Empleados`
- Los índices están creados para mejorar el rendimiento
- La validación de datos se hace en el modelo Pydantic

