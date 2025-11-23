"""
Script para revisar y analizar tokens JWT
"""
import os
import sys
from datetime import datetime
from jose import jwt, JWTError
from auth import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def decodificar_token(token: str):
    """Decodificar y analizar un token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload, None
    except JWTError as e:
        return None, str(e)

def analizar_token(token: str):
    """Analizar un token JWT"""
    print("=" * 80)
    print("ANÁLISIS DE TOKEN JWT")
    print("=" * 80)
    
    # Decodificar sin verificar primero para ver el contenido
    try:
        payload_sin_verificar = jwt.decode(token, options={"verify_signature": False})
        print("\n📋 Contenido del Token (sin verificar firma):")
        print("-" * 80)
        for key, value in payload_sin_verificar.items():
            if key == "exp":
                exp_timestamp = value
                exp_date = datetime.fromtimestamp(exp_timestamp)
                ahora = datetime.now()
                tiempo_restante = exp_date - ahora
                print(f"  {key}: {value}")
                print(f"    Fecha de expiración: {exp_date.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"    Tiempo restante: {tiempo_restante}")
                if tiempo_restante.total_seconds() < 0:
                    print(f"    ⚠️  TOKEN EXPIRADO")
                elif tiempo_restante.total_seconds() < 3600:
                    print(f"    ⚠️  Expira en menos de 1 hora")
                else:
                    print(f"    ✅ Token válido")
            elif key == "sub":
                print(f"  {key}: {value} (ID de usuario)")
            else:
                print(f"  {key}: {value}")
    except Exception as e:
        print(f"❌ Error al decodificar token: {e}")
        return
    
    # Verificar token correctamente
    print("\n🔐 Verificación del Token:")
    print("-" * 80)
    payload, error = decodificar_token(token)
    
    if payload:
        print("✅ Token VÁLIDO")
        print(f"   Usuario ID: {payload.get('sub')}")
        print(f"   Expira: {datetime.fromtimestamp(payload.get('exp')).strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"❌ Token INVÁLIDO: {error}")
    
    print("\n" + "=" * 80)

def revisar_configuracion():
    """Revisar configuración de tokens"""
    print("=" * 80)
    print("CONFIGURACIÓN DE TOKENS")
    print("=" * 80)
    
    print(f"\n🔑 SECRET_KEY:")
    secret_key = SECRET_KEY
    if len(secret_key) < 32:
        print(f"   ⚠️  ADVERTENCIA: SECRET_KEY muy corta ({len(secret_key)} caracteres)")
        print(f"   Recomendación: Usar al menos 32 caracteres")
    else:
        print(f"   ✅ Longitud adecuada ({len(secret_key)} caracteres)")
    
    if secret_key == "tu-clave-secreta-super-segura-cambiar-en-produccion":
        print(f"   ⚠️  ADVERTENCIA: Usando SECRET_KEY por defecto")
        print(f"   Recomendación: Cambiar en producción")
    else:
        print(f"   ✅ SECRET_KEY personalizada")
    
    print(f"\n🔐 ALGORITHM: {ALGORITHM}")
    if ALGORITHM == "HS256":
        print(f"   ✅ Algoritmo seguro")
    else:
        print(f"   ⚠️  Verificar que el algoritmo sea seguro")
    
    print(f"\n⏱️  DURACIÓN DEL TOKEN:")
    minutos = ACCESS_TOKEN_EXPIRE_MINUTES
    horas = minutos / 60
    dias = minutos / 1440
    meses = minutos / 43200
    
    print(f"   {minutos} minutos")
    print(f"   {horas:.2f} horas")
    print(f"   {dias:.2f} días")
    print(f"   {meses:.2f} meses")
    
    if minutos < 60:
        print(f"   ✅ Duración corta (recomendado para producción)")
    elif minutos < 1440:
        print(f"   ⚠️  Duración media (1 día)")
    else:
        print(f"   ⚠️  Duración larga ({dias:.1f} días)")
        print(f"   Recomendación: Considerar refresh tokens para mejor seguridad")
    
    print("\n" + "=" * 80)

def main():
    """Función principal"""
    print("\n🔍 REVISIÓN DE TOKENS JWT\n")
    
    # Revisar configuración
    revisar_configuracion()
    
    # Solicitar token si se proporciona como argumento
    if len(sys.argv) > 1:
        token = sys.argv[1]
        analizar_token(token)
    else:
        print("\n💡 Para analizar un token específico, ejecuta:")
        print("   python revisar_tokens.py <token_jwt>")
        print("\n📝 Ejemplo:")
        print("   python revisar_tokens.py eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        print("\n🔍 Para obtener un token:")
        print("   1. Haz login en la aplicación")
        print("   2. Abre DevTools → Application → Local Storage")
        print("   3. Copia el valor de 'access_token'")
        print("   4. Ejecuta: python revisar_tokens.py <token>")

if __name__ == "__main__":
    main()

