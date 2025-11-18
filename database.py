import sqlite3
import os
from pathlib import Path

# Ruta de la base de datos
DB_PATH = Path(__file__).parent / "clinica_medica.db"

def get_db_connection():
    """Obtener una conexión a la base de datos SQLite"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
    return conn

def init_db():
    """Inicializar la base de datos y crear las tablas si no existen"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Crear tabla Medicos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Medicos (
            IdMedico INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT NOT NULL,
            Apellido TEXT NOT NULL,
            Especialidad TEXT NOT NULL,
            Telefono TEXT NOT NULL,
            Email TEXT NOT NULL
        )
    """)
    
    # Crear tabla Pacientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Pacientes (
            IdPaciente INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT NOT NULL,
            Apellido TEXT NOT NULL,
            FechaNacimiento TEXT NOT NULL,
            Genero TEXT NOT NULL,
            Telefono TEXT NOT NULL,
            Email TEXT NOT NULL,
            Direccion TEXT
        )
    """)
    
    # Crear tabla Citas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Citas (
            IdCita INTEGER PRIMARY KEY AUTOINCREMENT,
            IdPaciente INTEGER NOT NULL,
            IdMedico INTEGER NOT NULL,
            FechaCita TEXT NOT NULL,
            Motivo TEXT NOT NULL,
            Estado TEXT DEFAULT 'Programada',
            FOREIGN KEY (IdPaciente) REFERENCES Pacientes(IdPaciente),
            FOREIGN KEY (IdMedico) REFERENCES Medicos(IdMedico)
        )
    """)
    
    # Crear tabla Usuarios para autenticación JWT
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuarios (
            IdUsuario INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT NOT NULL UNIQUE,
            PasswordHash TEXT NOT NULL,
            Email TEXT NOT NULL UNIQUE,
            Rol TEXT DEFAULT 'usuario',
            Activo INTEGER DEFAULT 1,
            CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Crear tabla Empleados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Empleados (
            IdEmpleado INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT NOT NULL,
            Apellido TEXT NOT NULL,
            FechaNacimiento TEXT,
            Genero TEXT,
            Telefono TEXT NOT NULL,
            Email TEXT NOT NULL,
            Direccion TEXT,
            Cedula TEXT,
            Cargo TEXT NOT NULL,
            Departamento TEXT NOT NULL,
            FechaContratacion TEXT NOT NULL,
            Salario REAL,
            Estado TEXT DEFAULT 'activo',
            Foto TEXT,
            CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Crear tabla Asistencia
    cursor.execute("""
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
    """)
    
    # Crear índices para mejorar el rendimiento
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_asistencia_empleado 
        ON Asistencia(IdEmpleado)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_asistencia_fecha 
        ON Asistencia(Fecha)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_asistencia_empleado_fecha 
        ON Asistencia(IdEmpleado, Fecha)
    """)
    
    # Crear tabla Departamentos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Departamentos (
            IdDepartamento INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT NOT NULL,
            Descripcion TEXT,
            Responsable TEXT,
            Telefono TEXT,
            Email TEXT,
            Estado TEXT DEFAULT 'activo',
            CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Crear tabla Puestos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Puestos (
            IdPuesto INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT NOT NULL,
            IdDepartamento INTEGER NOT NULL,
            Nivel TEXT,
            Descripcion TEXT,
            SalarioMinimo REAL,
            SalarioMaximo REAL,
            Requisitos TEXT,
            Estado TEXT DEFAULT 'activo',
            CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (IdDepartamento) REFERENCES Departamentos(IdDepartamento)
        )
    """)
    
    # Crear tabla AsignacionesEmpleados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS AsignacionesEmpleados (
            IdAsignacion INTEGER PRIMARY KEY AUTOINCREMENT,
            IdEmpleado INTEGER NOT NULL,
            IdDepartamento INTEGER NOT NULL,
            IdPuesto INTEGER NOT NULL,
            FechaAsignacion TEXT DEFAULT CURRENT_DATE,
            Estado TEXT DEFAULT 'activo',
            CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (IdEmpleado) REFERENCES Empleados(IdEmpleado),
            FOREIGN KEY (IdDepartamento) REFERENCES Departamentos(IdDepartamento),
            FOREIGN KEY (IdPuesto) REFERENCES Puestos(IdPuesto)
        )
    """)
    
    # Crear tabla Contratos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Contratos (
            IdContrato INTEGER PRIMARY KEY AUTOINCREMENT,
            IdEmpleado INTEGER NOT NULL,
            TipoContrato TEXT NOT NULL,
            NumeroContrato TEXT,
            FechaInicio TEXT NOT NULL,
            FechaFin TEXT,
            Salario REAL NOT NULL,
            Moneda TEXT DEFAULT 'DOP',
            HorasSemana INTEGER,
            Descripcion TEXT,
            Condiciones TEXT,
            Estado TEXT DEFAULT 'vigente',
            FechaFirma TEXT,
            DocumentoUrl TEXT,
            Observaciones TEXT,
            CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (IdEmpleado) REFERENCES Empleados(IdEmpleado)
        )
    """)
    
    # Crear tabla Capacitaciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Capacitaciones (
            IdCapacitacion INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT NOT NULL,
            Descripcion TEXT,
            Tipo TEXT NOT NULL,
            Modalidad TEXT NOT NULL,
            DuracionHoras INTEGER,
            FechaInicio TEXT NOT NULL,
            FechaFin TEXT,
            Instructor TEXT,
            Lugar TEXT,
            Costo REAL,
            Estado TEXT DEFAULT 'programada',
            CapacidadMaxima INTEGER,
            Requisitos TEXT,
            Objetivos TEXT,
            Certificado INTEGER DEFAULT 0,
            CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Crear tabla AsignacionesCapacitacion
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS AsignacionesCapacitacion (
            IdAsignacion INTEGER PRIMARY KEY AUTOINCREMENT,
            IdCapacitacion INTEGER NOT NULL,
            IdEmpleado INTEGER NOT NULL,
            FechaAsignacion TEXT NOT NULL,
            Estado TEXT DEFAULT 'asignada',
            Calificacion REAL,
            Asistencia REAL,
            Observaciones TEXT,
            CertificadoUrl TEXT,
            FechaCompletacion TEXT,
            FechaEmisionCertificado TEXT,
            NumeroCertificado TEXT,
            CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (IdCapacitacion) REFERENCES Capacitaciones(IdCapacitacion),
            FOREIGN KEY (IdEmpleado) REFERENCES Empleados(IdEmpleado)
        )
    """)
    
    # Crear tabla CriteriosEvaluacion
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CriteriosEvaluacion (
            IdCriterio INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT NOT NULL,
            Descripcion TEXT,
            Peso REAL,
            TipoEscala TEXT NOT NULL,
            EscalaMinima REAL,
            EscalaMaxima REAL,
            Activo INTEGER DEFAULT 1,
            CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Crear tabla EvaluacionesDesempeno
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS EvaluacionesDesempeno (
            IdEvaluacion INTEGER PRIMARY KEY AUTOINCREMENT,
            IdEmpleado INTEGER NOT NULL,
            IdEvaluador INTEGER,
            TipoEvaluacion TEXT NOT NULL,
            Periodo TEXT NOT NULL,
            FechaEvaluacion TEXT NOT NULL,
            FechaInicioPeriodo TEXT,
            FechaFinPeriodo TEXT,
            Estado TEXT DEFAULT 'programada',
            CalificacionFinal REAL,
            Fortalezas TEXT,
            AreasMejora TEXT,
            ComentariosEvaluador TEXT,
            ComentariosEmpleado TEXT,
            PlanDesarrollo TEXT,
            FirmaEvaluador TEXT,
            FirmaEmpleado TEXT,
            FechaFirmaEvaluador TEXT,
            FechaFirmaEmpleado TEXT,
            CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (IdEmpleado) REFERENCES Empleados(IdEmpleado),
            FOREIGN KEY (IdEvaluador) REFERENCES Empleados(IdEmpleado)
        )
    """)
    
    # Crear tabla CriteriosEvaluados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CriteriosEvaluados (
            IdCriterioEvaluado INTEGER PRIMARY KEY AUTOINCREMENT,
            IdEvaluacion INTEGER NOT NULL,
            IdCriterio INTEGER NOT NULL,
            Calificacion REAL,
            Comentarios TEXT,
            Evidencias TEXT,
            CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (IdEvaluacion) REFERENCES EvaluacionesDesempeno(IdEvaluacion),
            FOREIGN KEY (IdCriterio) REFERENCES CriteriosEvaluacion(IdCriterio)
        )
    """)
    
    # Crear tabla ConceptosNomina
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ConceptosNomina (
            IdConcepto INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT NOT NULL,
            Descripcion TEXT,
            Tipo TEXT NOT NULL,
            TipoCalculo TEXT NOT NULL,
            Valor REAL NOT NULL,
            AplicaA TEXT NOT NULL,
            IdDepartamento INTEGER,
            IdPuesto INTEGER,
            IdEmpleado INTEGER,
            Activo INTEGER DEFAULT 1,
            Orden INTEGER,
            CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (IdDepartamento) REFERENCES Departamentos(IdDepartamento),
            FOREIGN KEY (IdPuesto) REFERENCES Puestos(IdPuesto),
            FOREIGN KEY (IdEmpleado) REFERENCES Empleados(IdEmpleado)
        )
    """)
    
    # Crear tabla Nominas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Nominas (
            IdNomina INTEGER PRIMARY KEY AUTOINCREMENT,
            Periodo TEXT NOT NULL,
            FechaInicio TEXT NOT NULL,
            FechaFin TEXT NOT NULL,
            FechaPago TEXT NOT NULL,
            TipoNomina TEXT NOT NULL,
            Estado TEXT DEFAULT 'borrador',
            TotalEmpleados INTEGER DEFAULT 0,
            TotalDevengado REAL DEFAULT 0,
            TotalDeducido REAL DEFAULT 0,
            TotalNeto REAL DEFAULT 0,
            Observaciones TEXT,
            FechaCreacion TEXT DEFAULT CURRENT_TIMESTAMP,
            FechaActualizacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Crear tabla DetallesNomina
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS DetallesNomina (
            IdDetalleNomina INTEGER PRIMARY KEY AUTOINCREMENT,
            IdNomina INTEGER NOT NULL,
            IdEmpleado INTEGER NOT NULL,
            SalarioBase REAL NOT NULL,
            HorasTrabajadas REAL,
            HorasExtras REAL,
            Bonificaciones REAL DEFAULT 0,
            Deducciones REAL DEFAULT 0,
            TotalDevengado REAL DEFAULT 0,
            TotalDeducido REAL DEFAULT 0,
            NetoAPagar REAL DEFAULT 0,
            Observaciones TEXT,
            CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (IdNomina) REFERENCES Nominas(IdNomina),
            FOREIGN KEY (IdEmpleado) REFERENCES Empleados(IdEmpleado)
        )
    """)
    
    # Crear tabla SolicitudesVacacion
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SolicitudesVacacion (
            IdSolicitudVacacion INTEGER PRIMARY KEY AUTOINCREMENT,
            IdEmpleado INTEGER NOT NULL,
            FechaInicio TEXT NOT NULL,
            FechaFin TEXT NOT NULL,
            DiasSolicitados INTEGER NOT NULL,
            Motivo TEXT,
            Estado TEXT DEFAULT 'pendiente',
            IdAprobador INTEGER,
            FechaAprobacion TEXT,
            ComentariosAprobador TEXT,
            FechaCreacion TEXT DEFAULT CURRENT_TIMESTAMP,
            FechaActualizacion TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (IdEmpleado) REFERENCES Empleados(IdEmpleado),
            FOREIGN KEY (IdAprobador) REFERENCES Usuarios(IdUsuario)
        )
    """)
    
    # Crear tabla SolicitudesPermiso
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SolicitudesPermiso (
            IdSolicitudPermiso INTEGER PRIMARY KEY AUTOINCREMENT,
            IdEmpleado INTEGER NOT NULL,
            TipoPermiso TEXT NOT NULL,
            FechaInicio TEXT NOT NULL,
            FechaFin TEXT,
            HorasSolicitadas INTEGER,
            DiasSolicitados INTEGER,
            Motivo TEXT NOT NULL,
            Estado TEXT DEFAULT 'pendiente',
            IdAprobador INTEGER,
            FechaAprobacion TEXT,
            ComentariosAprobador TEXT,
            FechaCreacion TEXT DEFAULT CURRENT_TIMESTAMP,
            FechaActualizacion TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (IdEmpleado) REFERENCES Empleados(IdEmpleado),
            FOREIGN KEY (IdAprobador) REFERENCES Usuarios(IdUsuario)
        )
    """)
    
    # Crear tabla BalanceVacaciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS BalanceVacaciones (
            IdBalance INTEGER PRIMARY KEY AUTOINCREMENT,
            IdEmpleado INTEGER NOT NULL,
            Periodo TEXT NOT NULL,
            DiasAsignados INTEGER NOT NULL,
            DiasTomados INTEGER DEFAULT 0,
            DiasPendientes INTEGER DEFAULT 0,
            DiasDisponibles INTEGER DEFAULT 0,
            DiasVencidos INTEGER,
            FechaVencimiento TEXT,
            CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (IdEmpleado) REFERENCES Empleados(IdEmpleado)
        )
    """)
    
    # Crear tabla CategoriasDocumento
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CategoriasDocumento (
            IdCategoria INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT NOT NULL,
            Descripcion TEXT,
            Icono TEXT,
            Color TEXT,
            Orden INTEGER,
            Activa INTEGER DEFAULT 1,
            CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Crear tabla Documentos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Documentos (
            IdDocumento INTEGER PRIMARY KEY AUTOINCREMENT,
            Titulo TEXT NOT NULL,
            Descripcion TEXT,
            Categoria TEXT NOT NULL,
            TipoDocumento TEXT NOT NULL,
            Version TEXT NOT NULL,
            ArchivoUrl TEXT,
            ArchivoNombre TEXT,
            TamañoArchivo INTEGER,
            Estado TEXT DEFAULT 'borrador',
            Visibilidad TEXT DEFAULT 'publico',
            Tags TEXT,
            IdCreador INTEGER,
            IdDepartamento INTEGER,
            FechaCreacion TEXT DEFAULT CURRENT_TIMESTAMP,
            FechaActualizacion TEXT DEFAULT CURRENT_TIMESTAMP,
            FechaPublicacion TEXT,
            FechaVencimiento TEXT,
            Observaciones TEXT,
            FOREIGN KEY (IdCreador) REFERENCES Usuarios(IdUsuario),
            FOREIGN KEY (IdDepartamento) REFERENCES Departamentos(IdDepartamento)
        )
    """)
    
    # Crear tabla VersionesDocumento
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS VersionesDocumento (
            IdVersion INTEGER PRIMARY KEY AUTOINCREMENT,
            IdDocumento INTEGER NOT NULL,
            Version TEXT NOT NULL,
            Cambios TEXT,
            ArchivoUrl TEXT,
            ArchivoNombre TEXT,
            TamañoArchivo INTEGER,
            IdCreador INTEGER,
            FechaCreacion TEXT DEFAULT CURRENT_TIMESTAMP,
            EsVersionActual INTEGER DEFAULT 1,
            FOREIGN KEY (IdDocumento) REFERENCES Documentos(IdDocumento),
            FOREIGN KEY (IdCreador) REFERENCES Usuarios(IdUsuario)
        )
    """)
    
    # Crear tabla HistorialDocumento
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS HistorialDocumento (
            IdHistorial INTEGER PRIMARY KEY AUTOINCREMENT,
            IdDocumento INTEGER NOT NULL,
            Accion TEXT NOT NULL,
            IdUsuario INTEGER,
            Comentarios TEXT,
            FechaAccion TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (IdDocumento) REFERENCES Documentos(IdDocumento),
            FOREIGN KEY (IdUsuario) REFERENCES Usuarios(IdUsuario)
        )
    """)
    
    # Crear tabla Roles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Roles (
            IdRol INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT NOT NULL UNIQUE,
            Descripcion TEXT,
            Activo INTEGER DEFAULT 1,
            FechaCreacion TEXT DEFAULT CURRENT_TIMESTAMP,
            FechaActualizacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Crear tabla Permisos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Permisos (
            IdPermiso INTEGER PRIMARY KEY AUTOINCREMENT,
            Nombre TEXT NOT NULL UNIQUE,
            Descripcion TEXT,
            Modulo TEXT NOT NULL,
            Accion TEXT NOT NULL,
            Activo INTEGER DEFAULT 1,
            CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Crear tabla RolesPermisos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS RolesPermisos (
            IdRolPermiso INTEGER PRIMARY KEY AUTOINCREMENT,
            IdRol INTEGER NOT NULL,
            IdPermiso INTEGER NOT NULL,
            CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (IdRol) REFERENCES Roles(IdRol),
            FOREIGN KEY (IdPermiso) REFERENCES Permisos(IdPermiso),
            UNIQUE(IdRol, IdPermiso)
        )
    """)
    
    # Crear tabla HistorialUsuario
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS HistorialUsuario (
            IdHistorial INTEGER PRIMARY KEY AUTOINCREMENT,
            IdUsuario INTEGER NOT NULL,
            Accion TEXT NOT NULL,
            IpAddress TEXT,
            UserAgent TEXT,
            FechaAccion TEXT DEFAULT CURRENT_TIMESTAMP,
            Detalles TEXT,
            FOREIGN KEY (IdUsuario) REFERENCES Usuarios(IdUsuario)
        )
    """)
    
    # Crear índices adicionales para mejorar el rendimiento
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_contratos_empleado ON Contratos(IdEmpleado)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_contratos_estado ON Contratos(Estado)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_capacitaciones_estado ON Capacitaciones(Estado)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_evaluaciones_empleado ON EvaluacionesDesempeno(IdEmpleado)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nominas_periodo ON Nominas(Periodo)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vacaciones_empleado ON SolicitudesVacacion(IdEmpleado)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vacaciones_estado ON SolicitudesVacacion(Estado)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_documentos_categoria ON Documentos(Categoria)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_documentos_estado ON Documentos(Estado)")
    
    # Nota: El usuario administrador se crea en init_admin_user() después de importar auth
    
    conn.commit()
    conn.close()
    print(f"✅ Base de datos inicializada en: {DB_PATH}")

