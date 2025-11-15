# 🔗 ENDPOINTS API - TODAS LAS TABLAS

## 📌 URL Base
```
http://127.0.0.1:8001
```

---

## 👥 PACIENTES

### 1. Obtener todos los pacientes
```http
GET /pacientes/
```

**Ejemplo:**
```bash
curl http://127.0.0.1:8001/pacientes/
```

---

### 2. Obtener paciente por ID
```http
GET /pacientes/{id}
```

**Ejemplo:**
```bash
curl http://127.0.0.1:8001/pacientes/1
```

---

### 3. Crear nuevo paciente
```http
POST /pacientes/
Content-Type: application/json

{
  "Nombre": "María",
  "Apellido": "González",
  "FechaNacimiento": "1990-05-15",
  "Sexo": "F",
  "Telefono": "0987654321",
  "Direccion": "Calle Principal 123",
  "Email": "maria@email.com"
}
```

**Ejemplo con curl:**
```bash
curl -X POST http://127.0.0.1:8001/pacientes/ \
  -H "Content-Type: application/json" \
  -d '{"Nombre":"Juan","Apellido":"Pérez","FechaNacimiento":"1985-03-20","Sexo":"M","Telefono":"0998765432","Direccion":"Av. Central 456","Email":"juan@email.com"}'
```

---

### 4. Crear múltiples pacientes
```http
POST /pacientes/bulk
Content-Type: application/json

[
  {
    "Nombre": "Carlos",
    "Apellido": "López",
    "FechaNacimiento": "1992-07-10",
    "Sexo": "M",
    "Telefono": "0999999999",
    "Direccion": "Calle 5 789",
    "Email": "carlos@email.com"
  },
  {
    "Nombre": "Ana",
    "Apellido": "Martínez",
    "FechaNacimiento": "1988-12-05",
    "Sexo": "F",
    "Telefono": "0988888888",
    "Direccion": "Calle 10 321",
    "Email": "ana@email.com"
  }
]
```

---

### 5. Actualizar paciente
```http
PUT /pacientes/{id}
Content-Type: application/json

{
  "Nombre": "María",
  "Apellido": "González",
  "FechaNacimiento": "1990-05-15",
  "Sexo": "F",
  "Telefono": "0987654321",
  "Direccion": "Calle Nueva 999",
  "Email": "maria.new@email.com"
}
```

**Ejemplo:**
```bash
curl -X PUT http://127.0.0.1:8001/pacientes/1 \
  -H "Content-Type: application/json" \
  -d '{"Nombre":"María","Apellido":"González","FechaNacimiento":"1990-05-15","Sexo":"F","Telefono":"0987654321","Direccion":"Calle Nueva 999","Email":"maria.new@email.com"}'
```

---

### 6. Eliminar paciente
```http
DELETE /pacientes/{id}
```

**Ejemplo:**
```bash
curl -X DELETE http://127.0.0.1:8001/pacientes/1
```

---

## 👨‍⚕️ MEDICOS

### 1. Obtener todos los médicos
```http
GET /medicos/
```

**Ejemplo:**
```bash
curl http://127.0.0.1:8001/medicos/
```

---

### 2. Obtener médico por ID
```http
GET /medicos/{id}
```

**Ejemplo:**
```bash
curl http://127.0.0.1:8001/medicos/1
```

---

### 3. Crear nuevo médico
```http
POST /medicos/
Content-Type: application/json

{
  "Nombre": "Juan",
  "Apellido": "Pérez",
  "Especialidad": "Cardiología",
  "Telefono": "1234567890",
  "Email": "juan.perez@clinica.com"
}
```

**Ejemplo:**
```bash
curl -X POST http://127.0.0.1:8001/medicos/ \
  -H "Content-Type: application/json" \
  -d '{"Nombre":"Carlos","Apellido":"López","Especialidad":"Neurología","Telefono":"0987654321","Email":"carlos.lopez@clinica.com"}'
```

---

### 4. Actualizar médico
```http
PUT /medicos/{id}
Content-Type: application/json

{
  "Nombre": "Juan",
  "Apellido": "Pérez",
  "Especialidad": "Cardiología",
  "Telefono": "1234567890",
  "Email": "juan.perez@clinica.com"
}
```

**Ejemplo:**
```bash
curl -X PUT http://127.0.0.1:8001/medicos/1 \
  -H "Content-Type: application/json" \
  -d '{"Nombre":"Juan","Apellido":"Pérez","Especialidad":"Cirugía Cardíaca","Telefono":"1234567890","Email":"juan.perez@clinica.com"}'
```

---

### 5. Eliminar médico
```http
DELETE /medicos/{id}
```

**Ejemplo:**
```bash
curl -X DELETE http://127.0.0.1:8001/medicos/1
```

---

## 📅 CITAS

### 1. Obtener todas las citas
```http
GET /citas/
```

**Ejemplo:**
```bash
curl http://127.0.0.1:8001/citas/
```

---

### 2. Obtener cita por ID
```http
GET /citas/{id}
```

**Ejemplo:**
```bash
curl http://127.0.0.1:8001/citas/1
```

---

### 3. Crear nueva cita
```http
POST /citas/
Content-Type: application/json

{
  "IdPaciente": 1,
  "IdMedico": 1,
  "FechaCita": "2024-01-15T10:00:00",
  "Motivo": "Consulta general",
  "Estado": "Programada"
}
```

**Ejemplo:**
```bash
curl -X POST http://127.0.0.1:8001/citas/ \
  -H "Content-Type: application/json" \
  -d '{"IdPaciente":1,"IdMedico":1,"FechaCita":"2024-01-20T14:30:00","Motivo":"Revisión cardíaca","Estado":"Programada"}'
```

---

### 4. Actualizar cita
```http
PUT /citas/{id}
Content-Type: application/json

{
  "IdPaciente": 1,
  "IdMedico": 1,
  "FechaCita": "2024-01-15T10:00:00",
  "Motivo": "Consulta general",
  "Estado": "Completada"
}
```

**Ejemplo:**
```bash
curl -X PUT http://127.0.0.1:8001/citas/1 \
  -H "Content-Type: application/json" \
  -d '{"IdPaciente":1,"IdMedico":1,"FechaCita":"2024-01-20T14:30:00","Motivo":"Revisión cardíaca","Estado":"Completada"}'
```

---

### 5. Eliminar cita
```http
DELETE /citas/{id}
```

**Ejemplo:**
```bash
curl -X DELETE http://127.0.0.1:8001/citas/1
```

---

## 🩺 DIAGNOSTICOS

### 1. Obtener todos los diagnósticos
```http
GET /diagnosticos/
```

**Ejemplo:**
```bash
curl http://127.0.0.1:8001/diagnosticos/
```

---

### 2. Obtener diagnóstico por ID
```http
GET /diagnosticos/{id}
```

**Ejemplo:**
```bash
curl http://127.0.0.1:8001/diagnosticos/1
```

---

### 3. Obtener diagnósticos de un paciente
```http
GET /diagnosticos/paciente/{id_paciente}
```

**Ejemplo:**
```bash
curl http://127.0.0.1:8001/diagnosticos/paciente/1
```

---

### 4. Crear nuevo diagnóstico
```http
POST /diagnosticos/
Content-Type: application/json

{
  "IdPaciente": 1,
  "Descripcion": "Hipertensión arterial",
  "FechaDiagnostico": "2024-01-15",
  "CodigoICD10": "I10"
}
```

**Ejemplo con curl:**
```bash
curl -X POST http://127.0.0.1:8001/diagnosticos/ \
  -H "Content-Type: application/json" \
  -d '{"IdPaciente":1,"Descripcion":"Diabetes tipo 2","FechaDiagnostico":"2024-01-10","CodigoICD10":"E11"}'
```

---

### 5. Actualizar diagnóstico
```http
PUT /diagnosticos/{id}
Content-Type: application/json

{
  "IdPaciente": 1,
  "Descripcion": "Hipertensión arterial controlada",
  "FechaDiagnostico": "2024-01-15",
  "CodigoICD10": "I10"
}
```

**Ejemplo:**
```bash
curl -X PUT http://127.0.0.1:8001/diagnosticos/1 \
  -H "Content-Type: application/json" \
  -d '{"IdPaciente":1,"Descripcion":"Hipertensión arterial controlada","FechaDiagnostico":"2024-01-15","CodigoICD10":"I10"}'
```

---

### 6. Eliminar diagnóstico
```http
DELETE /diagnosticos/{id}
```

**Ejemplo:**
```bash
curl -X DELETE http://127.0.0.1:8001/diagnosticos/1
```

---

## 💊 TRATAMIENTOS

### 1. Obtener todos los tratamientos
```http
GET /tratamientos/
```

**Ejemplo:**
```bash
curl http://127.0.0.1:8001/tratamientos/
```

---

### 2. Obtener tratamiento por ID
```http
GET /tratamientos/{id}
```

**Ejemplo:**
```bash
curl http://127.0.0.1:8001/tratamientos/1
```

---

### 3. Obtener tratamientos de un diagnóstico
```http
GET /tratamientos/diagnostico/{id_diagnostico}
```

**Ejemplo:**
```bash
curl http://127.0.0.1:8001/tratamientos/diagnostico/1
```

---

### 4. Crear nuevo tratamiento
```http
POST /tratamientos/
Content-Type: application/json

{
  "IdDiagnostico": 1,
  "Descripcion": "Antihipertensivo oral",
  "FechaInicio": "2024-01-15",
  "FechaFin": "2024-06-15",
  "Medicamentos": "Losartán 50mg diarios"
}
```

**Ejemplo con curl:**
```bash
curl -X POST http://127.0.0.1:8001/tratamientos/ \
  -H "Content-Type: application/json" \
  -d '{"IdDiagnostico":1,"Descripcion":"Medicamento para diabetes","FechaInicio":"2024-01-10","FechaFin":"2024-12-31","Medicamentos":"Metformina 500mg dos veces al día"}'
```

---

### 5. Actualizar tratamiento
```http
PUT /tratamientos/{id}
Content-Type: application/json

{
  "IdDiagnostico": 1,
  "Descripcion": "Antihipertensivo oral ajustado",
  "FechaInicio": "2024-01-15",
  "FechaFin": "2024-12-31",
  "Medicamentos": "Losartán 100mg diarios"
}
```

**Ejemplo:**
```bash
curl -X PUT http://127.0.0.1:8001/tratamientos/1 \
  -H "Content-Type: application/json" \
  -d '{"IdDiagnostico":1,"Descripcion":"Antihipertensivo oral ajustado","FechaInicio":"2024-01-15","FechaFin":"2024-12-31","Medicamentos":"Losartán 100mg diarios"}'
```

---

### 6. Eliminar tratamiento
```http
DELETE /tratamientos/{id}
```

**Ejemplo:**
```bash
curl -X DELETE http://127.0.0.1:8001/tratamientos/1
```

---

## 🧪 PRUEBAS CON POWERSHELL

### Obtener todos los pacientes
```powershell
$response = curl http://127.0.0.1:8001/pacientes/
$response | ConvertFrom-Json | Format-List
```

### Crear un nuevo paciente
```powershell
$body = @{
    Nombre = "Roberto"
    Apellido = "Sánchez"
    FechaNacimiento = "1995-08-10"
    Sexo = "M"
    Telefono = "0999999999"
    Direccion = "Calle 123 456"
    Email = "roberto@email.com"
} | ConvertTo-Json

curl -X POST http://127.0.0.1:8001/pacientes/ `
  -H "Content-Type: application/json" `
  -Body $body | ConvertFrom-Json
```

### Obtener health check
```powershell
curl http://127.0.0.1:8001/health | ConvertFrom-Json
```

---

## 📖 DOCUMENTACIÓN INTERACTIVA

Puedes probar todos los endpoints de forma interactiva en:

- **Swagger UI**: http://127.0.0.1:8001/docs
- **ReDoc**: http://127.0.0.1:8001/redoc

---

## ⚙️ CÓDIGOS DE RESPUESTA

| Código | Significado |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado exitosamente |
| 404 | Not Found - Recurso no encontrado |
| 422 | Unprocessable Entity - Error de validación |
| 500 | Internal Server Error - Error del servidor |

---

## 💡 NOTAS IMPORTANTES

1. **Fechas**: Usar formato ISO 8601 (`YYYY-MM-DDTHH:mm:ss`)
2. **IDs**: Usar valores numéricos enteros
3. **Email**: Debe ser válido
4. **Teléfono**: Campo opcional
5. **Claves foráneas**: IdPaciente y IdMedico deben existir en la BD

---

## 🚀 Próximas Mejoras

- [ ] Endpoints para Diagnosticos
- [ ] Endpoints para Tratamientos
- [ ] Filtrado y búsqueda
- [ ] Paginación
- [ ] Autenticación JWT
- [ ] Rate limiting

¡Tu API está lista para usar! 🎉
