"""
Generar certificado SSL autofirmado usando Python (sin necesidad de OpenSSL)
"""
import subprocess
import sys
from pathlib import Path

def generar_certificado_python():
    """Generar certificado usando Python cryptography"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from datetime import datetime, timedelta
    except ImportError:
        print("=" * 80)
        print("ERROR: Biblioteca 'cryptography' no encontrada")
        print("=" * 80)
        print("\nInstala la biblioteca con:")
        print("  pip install cryptography")
        print("\nO usa OpenSSL directamente:")
        print("  Windows: generar_certificado_ssl.bat")
        print("  Linux/Mac: bash generar_certificado_ssl.sh")
        return False
    
    certs_dir = Path(__file__).parent / "certs"
    certs_dir.mkdir(exist_ok=True)
    
    key_file = certs_dir / "key.pem"
    cert_file = certs_dir / "cert.pem"
    
    print("=" * 80)
    print("GENERANDO CERTIFICADO SSL AUTOFIRMADO")
    print("=" * 80)
    
    # Generar clave privada
    print("\n1. Generando clave privada...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )
    
    # Guardar clave privada
    with open(key_file, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Crear certificado
    print("2. Generando certificado...")
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "DO"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Distrito Nacional"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Santo Domingo"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Clinica Medica"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.now(datetime.UTC)
    ).not_valid_after(
        datetime.now(datetime.UTC) + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.DNSName("127.0.0.1"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Guardar certificado
    with open(cert_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    # Dar permisos seguros (solo en Unix)
    import os
    if os.name != 'nt':
        os.chmod(key_file, 0o600)
        os.chmod(cert_file, 0o600)
    
    print("3. Certificado generado exitosamente!")
    print(f"\n   Certificado: {cert_file}")
    print(f"   Clave: {key_file}")
    print("\n" + "=" * 80)
    print("\nPara iniciar el servidor con HTTPS:")
    print("  python iniciar_servidor.py")
    print("\nO manualmente:")
    print("  uvicorn main:app --reload --host 0.0.0.0 --port 8443 \\")
    print("    --ssl-keyfile certs/key.pem --ssl-certfile certs/cert.pem")
    print("\n" + "=" * 80)
    
    return True

if __name__ == "__main__":
    import ipaddress
    try:
        generar_certificado_python()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nAsegúrate de tener 'cryptography' instalado:")
        print("  pip install cryptography")

