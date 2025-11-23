"""
Script para verificar qué rutas están disponibles en el servidor
"""
import requests
import json

def verificar_rutas():
    """Verificar qué rutas están disponibles"""
    base_url = "http://localhost:8000"
    
    print("=" * 80)
    print("VERIFICACION DE RUTAS DISPONIBLES")
    print("=" * 80)
    
    # Lista de endpoints a verificar
    endpoints = [
        ("GET", "/", "Root"),
        ("GET", "/health", "Health Check"),
        ("GET", "/docs", "Swagger UI"),
        ("POST", "/auth/login", "Login"),
        ("POST", "/auth/register", "Register"),
        ("GET", "/auth/me", "Get Current User"),
        ("GET", "/empleados", "Get Empleados"),
        ("GET", "/pacientes", "Get Pacientes"),
    ]
    
    print("\nProbando endpoints...\n")
    
    for method, endpoint, descripcion in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, timeout=3)
            else:
                # Para POST, enviamos un body vacío o mínimo
                if endpoint == "/auth/login":
                    response = requests.post(url, json={"username": "test", "password": "test"}, timeout=3)
                else:
                    response = requests.post(url, json={}, timeout=3)
            
            status = response.status_code
            if status == 200 or status == 201:
                estado = "[OK]"
            elif status == 404:
                estado = "[NO ENCONTRADO]"
            elif status == 401:
                estado = "[REQUIERE AUTH]"
            elif status == 422:
                estado = "[VALIDACION]"
            else:
                estado = f"[{status}]"
            
            print(f"{estado} {method:6} {endpoint:30} - {descripcion}")
            
        except requests.exceptions.ConnectionError:
            print(f"[SIN CONEXION] {method:6} {endpoint:30} - Backend no esta corriendo")
            break
        except Exception as e:
            print(f"[ERROR] {method:6} {endpoint:30} - {str(e)}")
    
    print("\n" + "=" * 80)
    print("INSTRUCCIONES")
    print("=" * 80)
    print("\nSi /auth/login muestra [NO ENCONTRADO]:")
    print("1. Detener el servidor backend (Ctrl+C)")
    print("2. Reiniciar con: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("3. Verificar que aparezca en Swagger: http://localhost:8000/docs")
    print("\nSi el backend no esta corriendo:")
    print("1. cd Proyecto-Base-de-Datos-2")
    print("2. uvicorn main:app --reload --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    verificar_rutas()

