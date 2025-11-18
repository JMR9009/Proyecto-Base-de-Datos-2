# 📋 Plan de Conexión Frontend-Backend

## ✅ Estado Actual

### Routers Existentes:
- ✅ `auth_router.py` - Autenticación (Login, Register, /me)
- ✅ `cita_router.py` - Citas médicas
- ✅ `empleado_router.py` - Empleados
- ✅ `asistencia_router.py` - Asistencia

### Routers Faltantes:
- ❌ `paciente_router.py` - Pacientes
- ❌ `medico_router.py` - Médicos
- ❌ `departamento_router.py` - Departamentos
- ❌ `puesto_router.py` - Puestos
- ❌ `asignacion_router.py` - Asignaciones de empleados
- ❌ `contrato_router.py` - Contratos
- ❌ `capacitacion_router.py` - Capacitaciones
- ❌ `asignacion_capacitacion_router.py` - Asignaciones de capacitación
- ❌ `evaluacion_desempeno_router.py` - Evaluaciones de desempeño
- ❌ `criterio_evaluacion_router.py` - Criterios de evaluación
- ❌ `nomina_router.py` - Nómina
- ❌ `concepto_nomina_router.py` - Conceptos de nómina
- ❌ `vacacion_router.py` - Vacaciones
- ❌ `permiso_router.py` - Permisos
- ❌ `balance_vacacion_router.py` - Balance de vacaciones
- ❌ `documento_router.py` - Documentación
- ❌ `version_documento_router.py` - Versiones de documentos
- ❌ `categoria_documento_router.py` - Categorías de documentos
- ❌ `usuario_router.py` - Usuarios (CRUD)
- ❌ `rol_router.py` - Roles
- ❌ `permiso_router.py` - Permisos del sistema

## 📊 Tablas Necesarias en Base de Datos

### Ya Existentes:
- ✅ Usuarios
- ✅ Empleados
- ✅ Asistencia
- ✅ Medicos
- ✅ Pacientes
- ✅ Citas

### Faltantes:
- ❌ Departamentos
- ❌ Puestos
- ❌ AsignacionesEmpleados
- ❌ Contratos
- ❌ Capacitaciones
- ❌ AsignacionesCapacitacion
- ❌ EvaluacionesCapacitacion
- ❌ CriteriosEvaluacion
- ❌ EvaluacionesDesempeno
- ❌ CriteriosEvaluados
- ❌ ConceptosNomina
- ❌ Nominas
- ❌ DetallesNomina
- ❌ SolicitudesVacacion
- ❌ SolicitudesPermiso
- ❌ BalanceVacaciones
- ❌ CategoriasDocumento
- ❌ Documentos
- ❌ VersionesDocumento
- ❌ HistorialDocumento
- ❌ Roles
- ❌ Permisos
- ❌ UsuariosRoles
- ❌ RolesPermisos
- ❌ HistorialUsuario

## 🎯 Orden de Implementación

1. **Pacientes y Médicos** (básicos, ya tienen tablas)
2. **Departamentos y Puestos** (base para otros módulos)
3. **Contratos** (depende de Empleados)
4. **Capacitación** (depende de Empleados)
5. **Evaluaciones** (depende de Empleados)
6. **Nómina** (depende de Empleados, Contratos)
7. **Vacaciones y Permisos** (depende de Empleados)
8. **Documentación** (independiente)
9. **Usuarios y Roles** (depende de Usuarios existente)

## 📝 Checklist

- [ ] Crear modelos Pydantic para todas las entidades
- [ ] Crear routers para todos los módulos
- [ ] Actualizar database.py con todas las tablas
- [ ] Registrar todos los routers en main.py
- [ ] Verificar que los endpoints coincidan con el frontend
- [ ] Probar cada vista del frontend

