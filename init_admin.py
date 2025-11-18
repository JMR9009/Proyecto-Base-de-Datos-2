"""
Script para inicializar usuario administrador
"""
from database import get_db_connection
from auth import get_password_hash

def init_admin_user():
    """Crear usuario administrador por defecto si no existe"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si el admin ya existe
        cursor.execute("SELECT COUNT(*) FROM Usuarios WHERE Username = 'admin'")
        if cursor.fetchone()[0] == 0:
            admin_password_hash = get_password_hash("admin123")
            cursor.execute("""
                INSERT INTO Usuarios (Username, PasswordHash, Email, Rol, Activo)
                VALUES (?, ?, ?, ?, ?)
            """, ("admin", admin_password_hash, "admin@clinica.com", "admin", 1))
            conn.commit()
            print("✅ Usuario administrador creado: admin / admin123")
        else:
            print("ℹ️  Usuario administrador ya existe")
    except Exception as e:
        print(f"⚠️  Error al crear usuario administrador: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_admin_user()

