"""
Script para probar el endpoint de login directamente
"""
import requests
import json

def probar_login():
    """Probar el endpoint de login"""
    url = "http://localhost:8000/auth/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    print("=" * 80)
    print("PRUEBA DEL ENDPOINT DE LOGIN")
    print("=" * 80)
    print(f"\nURL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    print("\nEnviando peticion...")
    
    try:
        response = requests.post(url, json=data, timeout=5)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n[OK] Login exitoso!")
        else:
            print(f"\n[ERROR] Login fallido con codigo {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] No se pudo conectar al servidor")
        print("        Verifica que el backend este corriendo en http://localhost:8000")
        print("\n        Ejecuta:")
        print("        cd Proyecto-Base-de-Datos-2")
        print("        uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    except requests.exceptions.Timeout:
        print("\n[ERROR] Timeout - El servidor no respondio a tiempo")
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {str(e)}")
    
    print("\n" + "=" * 80)
    
    # Probar también el endpoint de salud
    print("\nProbando endpoint de salud...")
    try:
        health_url = "http://localhost:8000/health"
        health_response = requests.get(health_url, timeout=5)
        print(f"Status Code: {health_response.status_code}")
        print(f"Response: {json.dumps(health_response.json(), indent=2)}")
    except Exception as e:
        print(f"[ERROR] No se pudo conectar al endpoint de salud: {str(e)}")

if __name__ == "__main__":
    probar_login()

