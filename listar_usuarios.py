"""
Script para listar todos los usuarios en la base de datos
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "clinica_medica.db"

def listar_usuarios():
    """Listar todos los usuarios de la base de datos"""
    print("=" * 80)
    print("USUARIOS EN LA BASE DE DATOS")
    print("=" * 80)
    
    if not DB_PATH.exists():
        print("[ERROR] La base de datos no existe")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Obtener todos los usuarios
    cursor.execute("""
        SELECT IdUsuario, Username, Email, Rol, Activo, CreatedAt 
        FROM Usuarios 
        ORDER BY IdUsuario
    """)
    users = cursor.fetchall()
    
    print(f"\nTotal de usuarios: {len(users)}\n")
    
    if len(users) == 0:
        print("No hay usuarios registrados en la base de datos.")
        print("El usuario administrador se creara automaticamente al iniciar el servidor.")
    else:
        for user in users:
            print(f"ID: {user[0]}")
            print(f"  Usuario: {user[1]}")
            print(f"  Email: {user[2]}")
            print(f"  Rol: {user[3]}")
            estado = "Activo" if user[4] else "Inactivo"
            print(f"  Estado: {estado}")
            print(f"  Fecha Creacion: {user[5]}")
            print("-" * 80)
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("CREDENCIALES POR DEFECTO")
    print("=" * 80)
    print("Usuario: admin")
    print("Contrasena: admin123")
    print("=" * 80)

if __name__ == "__main__":
    listar_usuarios()

