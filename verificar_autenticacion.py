"""
Script para verificar la configuración de autenticación
"""
from database import get_db_connection
from auth import get_password_hash, verify_password, create_access_token, verify_token
import json

def verificar_autenticacion():
    print("=" * 80)
    print("VERIFICACIÓN DE AUTENTICACIÓN")
    print("=" * 80)
    
    # 1. Verificar usuario admin
    print("\n1. Verificando usuario 'admin':")
    print("-" * 80)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT IdUsuario, Username, Email, Rol, Activo FROM Usuarios WHERE Username = 'admin'")
    admin = cursor.fetchone()
    
    if admin:
        print(f"[OK] Usuario admin encontrado:")
        print(f"   ID: {admin[0]}")
        print(f"   Username: {admin[1]}")
        print(f"   Email: {admin[2]}")
        print(f"   Rol: {admin[3]}")
        print(f"   Activo: {admin[4]} ({'[OK] Activo' if admin[4] == 1 else '[ERROR] Inactivo'})")
        
        if admin[4] != 1:
            print("\n[ADVERTENCIA] El usuario admin esta INACTIVO")
            print("   Esto causara errores 403 en todas las peticiones")
            print("   Solucion: UPDATE Usuarios SET Activo = 1 WHERE Username = 'admin';")
    else:
        print("[ERROR] Usuario admin NO encontrado")
        print("   Ejecuta init_admin.py para crearlo")
    
    # 2. Verificar contraseña
    print("\n2. Verificando contraseña:")
    print("-" * 80)
    if admin:
        cursor.execute("SELECT PasswordHash FROM Usuarios WHERE Username = 'admin'")
        password_hash = cursor.fetchone()[0]
        
        # Probar contraseña por defecto
        if verify_password("admin123", password_hash):
            print("[OK] La contraseña 'admin123' es correcta")
        else:
            print("[ERROR] La contraseña 'admin123' NO es correcta")
            print("   La contraseña puede haber sido cambiada")
    
    # 3. Generar token de prueba
    print("\n3. Generando token de prueba:")
    print("-" * 80)
    if admin:
        token = create_access_token(data={"sub": admin[0]})
        print(f"[OK] Token generado: {token[:50]}...")
        
        # Verificar token
        payload = verify_token(token)
        if payload:
            print(f"[OK] Token válido")
            print(f"   Payload: {json.dumps(payload, indent=2)}")
        else:
            print("[ERROR] Token inválido")
    
    # 4. Verificar todos los usuarios
    print("\n4. Listando todos los usuarios:")
    print("-" * 80)
    cursor.execute("SELECT IdUsuario, Username, Email, Rol, Activo FROM Usuarios")
    usuarios = cursor.fetchall()
    
    if usuarios:
        print(f"[OK] Total de usuarios: {len(usuarios)}")
        for usuario in usuarios:
            estado = "[OK] Activo" if usuario[4] == 1 else "[ERROR] Inactivo"
            print(f"   - {usuario[1]} ({usuario[2]}) - Rol: {usuario[3]} - {estado}")
    else:
        print("[ADVERTENCIA] No hay usuarios en la base de datos")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("RECOMENDACIONES")
    print("=" * 80)
    
    if admin and admin[4] != 1:
        print("\n[CRÍTICO] El usuario admin está INACTIVO")
        print("   Ejecuta este SQL para activarlo:")
        print("   UPDATE Usuarios SET Activo = 1 WHERE Username = 'admin';")
    
    print("\n[INFO] Para probar el login:")
    print("   1. Ve a http://localhost:3001/login")
    print("   2. Usuario: admin")
    print("   3. Contraseña: admin123")
    print("   4. Verifica que el token se guarde en Local Storage")
    print("   5. Intenta acceder a /empleados")

if __name__ == "__main__":
    verificar_autenticacion()

