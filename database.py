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
    
    # Nota: El usuario administrador se crea en init_admin_user() después de importar auth
    
    conn.commit()
    conn.close()
    print(f"✅ Base de datos inicializada en: {DB_PATH}")

