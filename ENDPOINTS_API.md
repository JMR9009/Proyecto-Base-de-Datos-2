# 📋 Endpoints de la API - Sistema de Gestión

## 🔗 Endpoints Globales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Información de la API |
| `GET` | `/health` | Estado de salud de la API y conexión a BD |
| `GET` | `/docs` | Documentación Swagger UI (solo desarrollo) |
| `GET` | `/redoc` | Documentación ReDoc (solo desarrollo) |

---

## 👥 Endpoints de Empleados (`/empleados`)

| Método | Endpoint | Descripción | Body |
|--------|----------|-------------|------|
| `GET` | `/empleados` | Obtener todos los empleados | - |
| `GET` | `/empleados/{id}` | Obtener empleado por ID | - |
| `POST` | `/empleados` | Crear nuevo empleado | Empleado |
| `PUT` | `/empleados/{id}` | Actualizar empleado existente | Empleado |
| `DELETE` | `/empleados/{id}` | Eliminar empleado | - |

### Modelo Empleado:
```json
{
  "Nombre": "string (requerido, 1-100 caracteres)",
  "Apellido": "string (requerido, 1-100 caracteres)",
  "FechaNacimiento": "string (opcional, formato YYYY-MM-DD)",
  "Genero": "string (opcional, max 20 caracteres)",
  "Telefono": "string (requerido, 8-20 caracteres)",
  "Email": "string (requerido, formato email)",
  "Direccion": "string (opcional, max 255 caracteres)",
  "Cedula": "string (opcional, max 20 caracteres)",
  "Cargo": "string (requerido, 1-100 caracteres)",
  "Departamento": "string (requerido, 1-100 caracteres)",
  "FechaContratacion": "string (requerido, formato YYYY-MM-DD)",
  "Salario": "float (opcional, >= 0)",
  "Estado": "string (default: 'activo', valores: activo/suspendido/retirado)",
  "Foto": "string (opcional, max 500 caracteres)"
}
```

---

## ⏰ Endpoints de Asistencia (`/asistencia`)

| Método | Endpoint | Descripción | Body |
|--------|----------|-------------|------|
| `GET` | `/asistencia` | Obtener todos los registros de asistencia | - |
| `GET` | `/asistencia/{id}` | Obtener registro por ID | - |
| `GET` | `/asistencia/empleado/{id_empleado}` | Obtener registros por empleado | - |
| `GET` | `/asistencia/fecha/{fecha}` | Obtener registros por fecha específica | - |
| `GET` | `/asistencia/rango?inicio={fecha}&fin={fecha}` | Obtener registros por rango de fechas | - |
| `POST` | `/asistencia` | Crear nuevo registro de asistencia | Asistencia |
| `POST` | `/asistencia/entrada` | Registrar entrada de empleado | Asistencia |
| `PUT` | `/asistencia/{id}/salida` | Registrar salida de empleado | {HoraSalida, HorasTrabajadas} |
| `PUT` | `/asistencia/{id}` | Actualizar registro de asistencia | Asistencia (parcial) |
| `DELETE` | `/asistencia/{id}` | Eliminar registro de asistencia | - |

### Modelo Asistencia:
```json
{
  "IdEmpleado": "integer (requerido, > 0)",
  "Fecha": "string (requerido, formato YYYY-MM-DD)",
  "HoraEntrada": "string (opcional, formato HH:mm)",
  "HoraSalida": "string (opcional, formato HH:mm)",
  "TipoRegistro": "string (requerido, valores: entrada/salida)",
  "TipoRegistroOrigen": "string (opcional, default: 'manual', valores: manual/biometrico)",
  "Estado": "string (default: 'presente', valores: presente/ausente/tardanza/permiso/vacaciones)",
  "Observaciones": "string (opcional, max 500 caracteres)",
  "Justificacion": "string (opcional, max 500 caracteres)",
  "HorasTrabajadas": "float (opcional, >= 0)",
  "Latitud": "float (opcional)",
  "Longitud": "float (opcional)"
}
```

### Ejemplo de registro de entrada:
```json
POST /asistencia/entrada
{
  "IdEmpleado": 1,
  "Fecha": "2024-01-15",
  "HoraEntrada": "08:00",
  "TipoRegistro": "entrada",
  "TipoRegistroOrigen": "biometrico",
  "Estado": "presente"
}
```

### Ejemplo de registro de salida:
```json
PUT /asistencia/{id}/salida
{
  "HoraSalida": "17:00",
  "HorasTrabajadas": 9.0
}
```

---

## 🏥 Endpoints de Pacientes (`/pacientes`)

| Método | Endpoint | Descripción | Body |
|--------|----------|-------------|------|
| `GET` | `/pacientes` | Obtener todos los pacientes | - |
| `GET` | `/pacientes/{id}` | Obtener paciente por ID | - |
| `POST` | `/pacientes` | Crear nuevo paciente | Paciente |
| `PUT` | `/pacientes/{id}` | Actualizar paciente existente | Paciente |
| `DELETE` | `/pacientes/{id}` | Eliminar paciente | - |

### Modelo Paciente:
```json
{
  "Nombre": "string (requerido, 1-100 caracteres)",
  "Apellido": "string (requerido, 1-100 caracteres)",
  "FechaNacimiento": "string (requerido, formato YYYY-MM-DD)",
  "Genero": "string (requerido, max 20 caracteres)",
  "Telefono": "string (requerido, 8-20 caracteres)",
  "Email": "string (requerido, formato email)",
  "Direccion": "string (opcional, max 255 caracteres)"
}
```

---

## 👨‍⚕️ Endpoints de Médicos (`/medicos`)

| Método | Endpoint | Descripción | Body |
|--------|----------|-------------|------|
| `GET` | `/medicos` | Obtener todos los médicos | - |
| `GET` | `/medicos/{id}` | Obtener médico por ID | - |
| `POST` | `/medicos` | Crear nuevo médico | Medico |
| `PUT` | `/medicos/{id}` | Actualizar médico existente | Medico |
| `DELETE` | `/medicos/{id}` | Eliminar médico | - |

### Modelo Medico:
```json
{
  "Nombre": "string (requerido, 1-100 caracteres)",
  "Apellido": "string (requerido, 1-100 caracteres)",
  "Especialidad": "string (requerido, 1-100 caracteres)",
  "Telefono": "string (requerido, 8-20 caracteres)",
  "Email": "string (requerido, formato email)"
}
```

---

## 📅 Endpoints de Citas (`/citas`)

| Método | Endpoint | Descripción | Body |
|--------|----------|-------------|------|
| `GET` | `/citas` | Obtener todas las citas | - |
| `GET` | `/citas/{id}` | Obtener cita por ID | - |
| `POST` | `/citas` | Crear nueva cita | Cita |
| `PUT` | `/citas/{id}` | Actualizar cita existente | Cita |
| `DELETE` | `/citas/{id}` | Eliminar cita | - |

### Modelo Cita:
```json
{
  "IdPaciente": "integer (requerido, > 0)",
  "IdMedico": "integer (requerido, > 0)",
  "FechaHora": "string (requerido, 10-50 caracteres)",
  "Motivo": "string (requerido, 1-500 caracteres)",
  "Estado": "string (default: 'Programada', max 50 caracteres)"
}
```

---

## 🔐 Endpoints de Autenticación (`/auth`)

Los endpoints de autenticación están definidos en `routers/auth_router.py`. Consulta ese archivo para ver los endpoints disponibles.

---

## 📝 Notas Importantes

### Códigos de Estado HTTP:
- `200 OK` - Operación exitosa
- `201 Created` - Recurso creado exitosamente
- `400 Bad Request` - Solicitud inválida
- `404 Not Found` - Recurso no encontrado
- `500 Internal Server Error` - Error del servidor
- `503 Service Unavailable` - Servicio no disponible

### Validaciones:
- Todos los endpoints validan los datos de entrada usando Pydantic
- Se sanitizan las entradas para prevenir XSS
- Se validan formatos de fecha (YYYY-MM-DD) y hora (HH:mm)
- Se validan relaciones entre entidades (ej: empleado debe existir para crear asistencia)

### Seguridad:
- Todos los endpoints están protegidos con middleware de seguridad
- Rate limiting aplicado
- Headers de seguridad configurados
- Validación de tipos de contenido

### Base de Datos:
- SQLite con archivo: `clinica_medica.db`
- Las tablas se crean automáticamente al iniciar la aplicación
- Índices creados para mejorar el rendimiento

---

## 🧪 Ejemplos de Uso

### Crear un empleado:
```bash
curl -X POST "http://localhost:8000/empleados" \
  -H "Content-Type: application/json" \
  -d '{
    "Nombre": "Juan",
    "Apellido": "Pérez",
    "Telefono": "8091234567",
    "Email": "juan.perez@example.com",
    "Cargo": "Desarrollador",
    "Departamento": "TI",
    "FechaContratacion": "2024-01-15",
    "Estado": "activo"
  }'
```

### Registrar entrada de asistencia:
```bash
curl -X POST "http://localhost:8000/asistencia/entrada" \
  -H "Content-Type: application/json" \
  -d '{
    "IdEmpleado": 1,
    "Fecha": "2024-01-15",
    "HoraEntrada": "08:00",
    "TipoRegistro": "entrada",
    "TipoRegistroOrigen": "biometrico",
    "Estado": "presente"
  }'
```

### Obtener asistencias por rango de fechas:
```bash
curl "http://localhost:8000/asistencia/rango?inicio=2024-01-01&fin=2024-01-31"
```

---

## 📚 Documentación Interactiva

Cuando el servidor esté en modo desarrollo, puedes acceder a:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

Estos proporcionan documentación interactiva de todos los endpoints con la capacidad de probarlos directamente desde el navegador.

