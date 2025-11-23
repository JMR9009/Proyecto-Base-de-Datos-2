"""
Script para iniciar el servidor FastAPI
Detecta automáticamente si usar HTTP o HTTPS según los certificados disponibles
"""
import subprocess
import sys
from pathlib import Path

def iniciar_servidor():
    """Iniciar servidor HTTP o HTTPS según disponibilidad"""
    certs_dir = Path(__file__).parent / "certs"
    key_file = certs_dir / "key.pem"
    cert_file = certs_dir / "cert.pem"
    
    # Verificar si hay certificados SSL
    usar_https = key_file.exists() and cert_file.exists()
    
    if usar_https:
        print("=" * 80)
        print("INICIANDO SERVIDOR CON HTTPS")
        print("=" * 80)
        print(f"\nCertificado SSL encontrado")
        print(f"Servidor: https://localhost:8443")
        print(f"Documentación: https://localhost:8443/docs")
        print("\n⚠️  Advertencia: Certificado autofirmado")
        print("   El navegador mostrará una advertencia. Esto es normal en desarrollo.")
        print("\n" + "=" * 80)
        
        cmd = [
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8443",
            "--ssl-keyfile", str(key_file),
            "--ssl-certfile", str(cert_file)
        ]
    else:
        print("=" * 80)
        print("INICIANDO SERVIDOR CON HTTP")
        print("=" * 80)
        print(f"\nServidor: http://localhost:8000")
        print(f"Documentación: http://localhost:8000/docs")
        print("\n💡 Para usar HTTPS, genera certificados con:")
        print("   Windows: generar_certificado_ssl.bat")
        print("   Linux/Mac: bash generar_certificado_ssl.sh")
        print("\n" + "=" * 80)
        
        cmd = [
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nServidor detenido.")

if __name__ == "__main__":
    iniciar_servidor()

