# Esquema de Arquitectura - API Clínica Médica

## 📐 Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENTE (Frontend)                    │
│                    (React, Vue, Angular, etc.)               │
└───────────────────────────┬───────────────────────────────────┘
                            │ HTTP/HTTPS
                            │ REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI APPLICATION                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              main.py (Punto de Entrada)              │  │
│  │  - Configuración de FastAPI                           │  │
│  │  - Middleware (CORS, Logging)                         │  │
│  │  - Health Check (/health)                             │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                        │
│  ┌───────────────────┴──────────────────────────────────┐  │
│  │                    ROUTERS                            │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │  │
│  │  │   Paciente   │  │   Médico    │  │    Cita     │ │  │
│  │  │   Router     │  │   Router    │  │   Router    │ │  │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘ │  │
│  └─────────┼──────────────────┼──────────────────┼────────┘  │
│            │                  │                  │           │
│  ┌─────────┴──────────────────┴──────────────────┴────────┐  │
│  │                    MODELS (Pydantic)                  │  │
│  │  - Validación de datos                                 │  │
│  │  - Serialización/Deserialización                      │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                        │                                      │
│  ┌─────────────────────┴────────────────────────────────┐  │
│  │              DATABASE LAYER                            │  │
│  │  - Gestión de conexiones                               │  │
│  │  - Ejecución de queries                                │  │
│  └───────────────────┬──────────────────────────────────┘  │
└────────────────────────┼──────────────────────────────────────┘
                         │
                         │ pyodbc
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  SQL SERVER DATABASE                         │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐     │
│  │  Pacientes   │  │   Medicos    │  │    Citas    │     │
│  │   Table      │  │   Table      │  │   Table     │     │
│  └──────────────┘  └──────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Estructura de Carpetas

```
Proyecto-Base-de-Datos-2/
│
├── main.py                    # 🚀 Punto de entrada de la aplicación
│   ├── Configuración FastAPI
│   ├── Middleware (CORS)
│   ├── Registro de routers
│   └── Endpoints globales (/health)
│
├── config.py                  # ⚙️ Configuración centralizada
│   ├── Variables de entorno
│   ├── Settings de BD
│   └── Configuración CORS
│
├── database.py                 # 🗄️ Capa de acceso a datos
│   ├── Clase Database
│   ├── Gestión de conexiones
│   └── Métodos de queries
│
├── exceptions.py              # ⚠️ Excepciones personalizadas
│   ├── DatabaseError
│   ├── NotFoundError
│   └── ValidationError
│
├── requirements.txt           # 📦 Dependencias del proyecto
│
├── Conexion SQL.py            # 🧪 Script de prueba de conexión
│
├── models/                    # 📋 Modelos Pydantic
│   ├── __init__.py
│   ├── paciente.py
│   │   ├── Paciente (input)
│   │   └── PacienteResponse (output)
│   ├── medico.py
│   │   ├── Medico (input)
│   │   └── MedicoResponse (output)
│   └── cita.py
│       ├── Cita (input)
│       └── CitaResponse (output)
│
└── routers/                   # 🛣️ Routers de FastAPI
    ├── __init__.py
    ├── paciente_router.py
    │   ├── GET /pacientes
    │   ├── GET /pacientes/{id}
    │   ├── POST /pacientes
    │   ├── POST /pacientes/bulk
    │   ├── PUT /pacientes/{id}
    │   └── DELETE /pacientes/{id}
    ├── medico_router.py
    │   ├── GET /medicos
    │   ├── GET /medicos/{id}
    │   ├── POST /medicos
    │   ├── PUT /medicos/{id}
    │   └── DELETE /medicos/{id}
    └── cita_router.py
        ├── GET /citas
        ├── GET /citas/{id}
        ├── POST /citas
        ├── PUT /citas/{id}
        └── DELETE /citas/{id}
```

## 🔄 Flujo de una Petición HTTP

```
1. Cliente envía petición HTTP
   │
   ▼
2. FastAPI recibe la petición
   │
   ▼
3. Middleware procesa (CORS, Logging)
   │
   ▼
4. Router correspondiente maneja la ruta
   │
   ▼
5. Validación con Pydantic Model
   │
   ▼
6. Database Layer ejecuta query
   │
   ▼
7. SQL Server procesa y retorna datos
   │
   ▼
8. Database Layer formatea respuesta
   │
   ▼
9. Router convierte a Response Model
   │
   ▼
10. FastAPI serializa a JSON
    │
    ▼
11. Cliente recibe respuesta HTTP
```

## 🎯 Endpoints Disponibles

### Endpoints Globales
```
GET  /              → Información de la API
GET  /health        → Estado de salud de la API
GET  /docs          → Documentación Swagger UI
GET  /redoc         → Documentación ReDoc
```

### Endpoints de Pacientes
```
GET    /pacientes           → Listar todos los pacientes
GET    /pacientes/{id}      → Obtener paciente por ID
POST   /pacientes           → Crear nuevo paciente
POST   /pacientes/bulk      → Crear múltiples pacientes
PUT    /pacientes/{id}      → Actualizar paciente
DELETE /pacientes/{id}      → Eliminar paciente
```

### Endpoints de Médicos
```
GET    /medicos           → Listar todos los médicos
GET    /medicos/{id}      → Obtener médico por ID
POST   /medicos           → Crear nuevo médico
PUT    /medicos/{id}      → Actualizar médico
DELETE /medicos/{id}      → Eliminar médico
```

### Endpoints de Citas
```
GET    /citas           → Listar todas las citas
GET    /citas/{id}      → Obtener cita por ID
POST   /citas           → Crear nueva cita
PUT    /citas/{id}      → Actualizar cita
DELETE /citas/{id}      → Eliminar cita
```

## 🔐 Capas de la Aplicación

### 1. Capa de Presentación (Routers)
- **Responsabilidad**: Manejar peticiones HTTP
- **Componentes**: `routers/*.py`
- **Funciones**:
  - Validar rutas
  - Llamar a la capa de servicio
  - Formatear respuestas HTTP

### 2. Capa de Validación (Models)
- **Responsabilidad**: Validar y transformar datos
- **Componentes**: `models/*.py`
- **Funciones**:
  - Validación de entrada
  - Serialización de salida
  - Esquemas de datos

### 3. Capa de Lógica de Negocio (Database)
- **Responsabilidad**: Operaciones de base de datos
- **Componentes**: `database.py`
- **Funciones**:
  - Gestión de conexiones
  - Ejecución de queries
  - Manejo de transacciones

### 4. Capa de Datos (SQL Server)
- **Responsabilidad**: Almacenamiento persistente
- **Componentes**: Tablas SQL Server
- **Funciones**:
  - Almacenar datos
  - Consultas complejas
  - Integridad referencial

## 📊 Diagrama de Secuencia (Ejemplo: Crear Paciente)

```
Cliente          Router          Model          Database        SQL Server
  │                │               │               │                │
  │ POST /pacientes│               │               │                │
  │───────────────>│               │               │                │
  │                │               │               │                │
  │                │ Validar datos │               │                │
  │                │──────────────>│               │                │
  │                │               │               │                │
  │                │ Datos válidos │               │                │
  │                │<──────────────│               │                │
  │                │               │               │                │
  │                │ INSERT query  │               │                │
  │                │───────────────┼──────────────>│                │
  │                │               │               │                │
  │                │               │               │ Ejecutar INSERT │
  │                │               │               │───────────────>│
  │                │               │               │                │
  │                │               │               │ Resultado OK   │
  │                │               │               │<───────────────│
  │                │               │               │                │
  │                │ Respuesta     │               │                │
  │                │<──────────────┼───────────────│                │
  │                │               │               │                │
  │ 201 Created    │               │               │                │
  │<───────────────│               │               │                │
```

## 🛠️ Stack Tecnológico

```
┌─────────────────────────────────────────┐
│         FRONTEND (Cliente)              │
│  - React / Vue / Angular / Mobile App  │
└─────────────────────────────────────────┘
                    │
                    │ HTTP/REST
                    ▼
┌─────────────────────────────────────────┐
│         BACKEND (FastAPI)               │
│  - Python 3.8+                         │
│  - FastAPI Framework                    │
│  - Pydantic (Validación)                │
│  - Uvicorn (ASGI Server)                │
└─────────────────────────────────────────┘
                    │
                    │ pyodbc
                    ▼
┌─────────────────────────────────────────┐
│         BASE DE DATOS                   │
│  - SQL Server                           │
│  - ODBC Driver 17                       │
└─────────────────────────────────────────┘
```

## 🔧 Componentes Clave

### Configuración (`config.py`)
- Variables de entorno
- Settings de conexión
- Configuración CORS

### Base de Datos (`database.py`)
- Pool de conexiones
- Métodos de query
- Manejo de transacciones

### Excepciones (`exceptions.py`)
- Errores personalizados
- Códigos HTTP apropiados
- Mensajes descriptivos

### Modelos (`models/`)
- Validación automática
- Documentación automática
- Type hints

### Routers (`routers/`)
- Endpoints RESTful
- Manejo de errores
- Documentación OpenAPI

## 📈 Escalabilidad

```
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Load Balancer  │
└──────┬──────────┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
┌─────┐ ┌─────┐
│ API │ │ API │  (Múltiples instancias)
└──┬──┘ └──┬──┘
   │       │
   └───┬───┘
       ▼
┌─────────────┐
│ SQL Server  │
│  (Clustered)│
└─────────────┘
```

## ✅ Buenas Prácticas Implementadas

- ✅ Separación de responsabilidades
- ✅ Configuración centralizada
- ✅ Manejo de errores robusto
- ✅ Validación de datos automática
- ✅ Documentación automática (OpenAPI)
- ✅ CORS configurado
- ✅ Logging estructurado
- ✅ Código reutilizable
- ✅ Type hints
- ✅ Health checks

