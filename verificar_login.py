"""
Script para verificar la configuración del login
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "clinica_medica.db"

def verificar_configuracion():
    """Verificar que todo esté configurado correctamente para el login"""
    print("=" * 60)
    print("VERIFICACIÓN DE CONFIGURACIÓN DE LOGIN")
    print("=" * 60)
    
    # 1. Verificar que la base de datos existe
    if not DB_PATH.exists():
        print("[ERROR] La base de datos no existe en:", DB_PATH)
        return False
    print("[OK] Base de datos existe:", DB_PATH)
    
    # 2. Verificar que la tabla Usuarios existe
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Usuarios'")
    if cursor.fetchone() is None:
        print("[ERROR] La tabla 'Usuarios' no existe")
        conn.close()
        return False
    print("[OK] Tabla 'Usuarios' existe")
    
    # 3. Verificar estructura de la tabla
    cursor.execute("PRAGMA table_info(Usuarios)")
    columns = [row[1] for row in cursor.fetchall()]
    required_columns = ['IdUsuario', 'Username', 'PasswordHash', 'Email', 'Rol', 'Activo']
    missing_columns = [col for col in required_columns if col not in columns]
    if missing_columns:
        print(f"[ERROR] Faltan columnas en la tabla: {missing_columns}")
        conn.close()
        return False
    print("[OK] Estructura de tabla correcta")
    print(f"   Columnas: {', '.join(columns)}")
    
    # 4. Verificar usuarios en la base de datos
    cursor.execute("SELECT COUNT(*) FROM Usuarios")
    user_count = cursor.fetchone()[0]
    print(f"[OK] Usuarios en la base de datos: {user_count}")
    
    if user_count == 0:
        print("[ADVERTENCIA] No hay usuarios en la base de datos")
        print("   El usuario administrador deberia crearse automaticamente al iniciar el servidor")
    else:
        # Mostrar usuarios
        cursor.execute("SELECT IdUsuario, Username, Email, Rol, Activo FROM Usuarios")
        users = cursor.fetchall()
        print("\nUsuarios registrados:")
        for user in users:
            estado = "[ACTIVO]" if user[4] else "[INACTIVO]"
            print(f"   - ID: {user[0]}, Usuario: {user[1]}, Email: {user[2]}, Rol: {user[3]}, {estado}")
    
    # 5. Verificar usuario admin específico
    cursor.execute("SELECT Username, PasswordHash FROM Usuarios WHERE Username = 'admin'")
    admin_user = cursor.fetchone()
    if admin_user:
        print(f"\n[OK] Usuario 'admin' existe")
        print(f"   PasswordHash: {'*' * 20} (hash bcrypt)")
    else:
        print("\n[ADVERTENCIA] Usuario 'admin' no encontrado")
        print("   Deberia crearse automaticamente al iniciar el servidor")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print("[OK] Base de datos: OK")
    print("[OK] Tabla Usuarios: OK")
    print("[OK] Estructura: OK")
    if user_count > 0:
        print("[OK] Usuarios: OK")
    else:
        print("[ADVERTENCIA] Usuarios: Pendiente (se crearan al iniciar el servidor)")
    
    return True

if __name__ == "__main__":
    verificar_configuracion()

