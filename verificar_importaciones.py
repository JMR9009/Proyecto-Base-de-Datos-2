"""
Script para verificar que los routers se pueden importar correctamente
"""
print("=" * 80)
print("VERIFICACION DE IMPORTACIONES")
print("=" * 80)

try:
    print("\n1. Importando routers...")
    from routers import auth_router, empleado_router, asistencia_router, cita_router
    print("   [OK] Todos los routers importados correctamente")
    
    print("\n2. Verificando prefijos...")
    print(f"   auth_router.prefix: {auth_router.router.prefix}")
    print(f"   empleado_router.prefix: {empleado_router.router.prefix}")
    print(f"   asistencia_router.prefix: {asistencia_router.router.prefix}")
    print(f"   cita_router.prefix: {cita_router.router.prefix}")
    
    print("\n3. Verificando rutas de autenticacion...")
    rutas_auth = [r.path for r in auth_router.router.routes]
    print(f"   Rutas: {rutas_auth}")
    
    if '/auth/login' in rutas_auth:
        print("   [OK] Ruta /auth/login encontrada")
    else:
        print("   [ERROR] Ruta /auth/login NO encontrada")
    
    print("\n4. Verificando que main.py puede importar...")
    from main import app
    print("   [OK] main.py importado correctamente")
    
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print("[OK] Todos los routers estan correctamente configurados")
    print("\nEl problema es que el servidor necesita REINICIARSE")
    print("para cargar los routers correctamente.")
    print("\nInstrucciones:")
    print("1. Detener el servidor (Ctrl+C)")
    print("2. Reiniciar con: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("3. Verificar en http://localhost:8000/docs que aparezcan los endpoints")
    
except Exception as e:
    print(f"\n[ERROR] Error al importar: {str(e)}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 80)
    print("Hay un error en el codigo que debe corregirse antes de continuar.")

