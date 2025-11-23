"""
Script para iniciar el servidor FastAPI con HTTPS
"""
import subprocess
import sys
import os
from pathlib import Path

def iniciar_servidor_https():
    """Iniciar servidor con HTTPS"""
    certs_dir = Path(__file__).parent / "certs"
    key_file = certs_dir / "key.pem"
    cert_file = certs_dir / "cert.pem"
    
    # Verificar que los certificados existan
    if not key_file.exists() or not cert_file.exists():
        print("=" * 80)
        print("ERROR: Certificados SSL no encontrados")
        print("=" * 80)
        print("\nGenera los certificados primero:")
        print("  Windows: generar_certificado_ssl.bat")
        print("  Linux/Mac: bash generar_certificado_ssl.sh")
        print("\nO ejecuta manualmente:")
        print("  openssl req -x509 -newkey rsa:4096 -nodes \\")
        print("    -keyout certs/key.pem -out certs/cert.pem -days 365 \\")
        print("    -subj \"/CN=localhost\"")
        return
    
    print("=" * 80)
    print("INICIANDO SERVIDOR CON HTTPS")
    print("=" * 80)
    print(f"\nCertificado: {cert_file}")
    print(f"Clave: {key_file}")
    print("\nServidor disponible en: https://localhost:8443")
    print("Documentación: https://localhost:8443/docs")
    print("\n⚠️  El navegador mostrará una advertencia de certificado autofirmado")
    print("   Esto es normal en desarrollo. Acepta la excepción para continuar.")
    print("\n" + "=" * 80)
    
    # Ejecutar uvicorn con HTTPS
    cmd = [
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8443",
        "--ssl-keyfile", str(key_file),
        "--ssl-certfile", str(cert_file)
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nServidor detenido.")

if __name__ == "__main__":
    iniciar_servidor_https()

