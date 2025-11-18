"""
Script para verificar la seguridad de los tokens JWT
"""
import os
from auth import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def verificar_seguridad():
    """Verificar aspectos de seguridad de los tokens"""
    print("=" * 80)
    print("VERIFICACIÓN DE SEGURIDAD DE TOKENS JWT")
    print("=" * 80)
    
    problemas = []
    advertencias = []
    correcto = []
    
    # 1. Verificar SECRET_KEY
    print("\n1. SECRET_KEY:")
    print("-" * 80)
    if SECRET_KEY == "tu-clave-secreta-super-segura-cambiar-en-produccion":
        problemas.append("SECRET_KEY es la clave por defecto - DEBE cambiarse en produccion")
        print("[PROBLEMA] Usando SECRET_KEY por defecto")
    else:
        correcto.append("SECRET_KEY personalizada")
        print("[OK] SECRET_KEY personalizada")
    
    if len(SECRET_KEY) < 32:
        problemas.append(f"SECRET_KEY muy corta ({len(SECRET_KEY)} caracteres) - Recomendado: minimo 32")
        print(f"[PROBLEMA] SECRET_KEY muy corta ({len(SECRET_KEY)} caracteres)")
    else:
        correcto.append(f"SECRET_KEY con longitud adecuada ({len(SECRET_KEY)} caracteres)")
        print(f"[OK] Longitud adecuada: {len(SECRET_KEY)} caracteres")
    
    # 2. Verificar ALGORITHM
    print("\n2. ALGORITHM:")
    print("-" * 80)
    algoritmos_seguros = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]
    if ALGORITHM in algoritmos_seguros:
        correcto.append(f"Algoritmo seguro: {ALGORITHM}")
        print(f"[OK] Algoritmo seguro: {ALGORITHM}")
    else:
        problemas.append(f"Algoritmo no reconocido como seguro: {ALGORITHM}")
        print(f"[PROBLEMA] Algoritmo no reconocido: {ALGORITHM}")
    
    # 3. Verificar duración del token
    print("\n3. DURACIÓN DEL TOKEN:")
    print("-" * 80)
    minutos = ACCESS_TOKEN_EXPIRE_MINUTES
    horas = minutos / 60
    dias = minutos / 1440
    
    print(f"   Duración: {minutos} minutos ({horas:.2f} horas, {dias:.2f} días)")
    
    if minutos < 15:
        advertencias.append("Token muy corto (< 15 min) - Puede causar problemas de UX")
        print("[ADVERTENCIA] Token muy corto")
    elif minutos < 60:
        correcto.append("Token de corta duracion (recomendado para produccion)")
        print("[OK] Duracion corta (recomendado para produccion)")
    elif minutos < 1440:
        advertencias.append("Token de duracion media (1 dia) - Considerar refresh tokens")
        print("[ADVERTENCIA] Duracion media - Considerar refresh tokens")
    else:
        advertencias.append(f"Token de larga duracion ({dias:.1f} dias) - Mayor riesgo si es robado")
        print(f"[ADVERTENCIA] Duracion larga ({dias:.1f} dias)")
    
    # 4. Verificar variables de entorno
    print("\n4. VARIABLES DE ENTORNO:")
    print("-" * 80)
    secret_key_env = os.getenv("SECRET_KEY")
    algorithm_env = os.getenv("ALGORITHM")
    expire_env = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    
    if secret_key_env:
        correcto.append("SECRET_KEY configurada desde variable de entorno")
        print("[OK] SECRET_KEY desde variable de entorno")
    else:
        advertencias.append("SECRET_KEY no esta en variable de entorno - Usando valor por defecto")
        print("[ADVERTENCIA] SECRET_KEY no esta en variable de entorno")
    
    if algorithm_env:
        correcto.append("ALGORITHM configurado desde variable de entorno")
        print("[OK] ALGORITHM desde variable de entorno")
    else:
        print("[INFO] ALGORITHM usando valor por defecto")
    
    if expire_env:
        correcto.append("ACCESS_TOKEN_EXPIRE_MINUTES configurado desde variable de entorno")
        print("[OK] ACCESS_TOKEN_EXPIRE_MINUTES desde variable de entorno")
    else:
        print("[INFO] ACCESS_TOKEN_EXPIRE_MINUTES usando valor por defecto")
    
    # 5. Verificar entorno de producción
    print("\n5. ENTORNO:")
    print("-" * 80)
    is_production = os.getenv("ENVIRONMENT", "development").lower() == "production"
    if is_production:
        print("[OK] Modo PRODUCCION")
        if SECRET_KEY == "tu-clave-secreta-super-segura-cambiar-en-produccion":
            problemas.append("CRITICO: En produccion con SECRET_KEY por defecto")
    else:
        print("[INFO] Modo DESARROLLO")
        if SECRET_KEY == "tu-clave-secreta-super-segura-cambiar-en-produccion":
            advertencias.append("SECRET_KEY por defecto - Aceptable en desarrollo")
    
    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN")
    print("=" * 80)
    
    if problemas:
        print(f"\n[PROBLEMAS] Encontrados ({len(problemas)}):")
        for i, problema in enumerate(problemas, 1):
            print(f"   {i}. {problema}")
    
    if advertencias:
        print(f"\n[ADVERTENCIAS] ({len(advertencias)}):")
        for i, advertencia in enumerate(advertencias, 1):
            print(f"   {i}. {advertencia}")
    
    if correcto:
        print(f"\n[OK] Configuraciones correctas ({len(correcto)}):")
        for i, item in enumerate(correcto, 1):
            print(f"   {i}. {item}")
    
    # Recomendaciones
    print("\n" + "=" * 80)
    print("RECOMENDACIONES")
    print("=" * 80)
    
    recomendaciones = []
    
    if SECRET_KEY == "tu-clave-secreta-super-segura-cambiar-en-produccion":
        recomendaciones.append("Cambiar SECRET_KEY en producción a una clave aleatoria fuerte")
    
    if len(SECRET_KEY) < 32:
        recomendaciones.append("Usar SECRET_KEY de al menos 32 caracteres")
    
    if ACCESS_TOKEN_EXPIRE_MINUTES > 1440:
        recomendaciones.append("Considerar implementar refresh tokens para tokens de larga duración")
    
    if not os.getenv("SECRET_KEY"):
        recomendaciones.append("Configurar SECRET_KEY como variable de entorno")
    
    if recomendaciones:
        for i, rec in enumerate(recomendaciones, 1):
            print(f"   {i}. {rec}")
    else:
        print("   [OK] No hay recomendaciones criticas")
    
    print("\n" + "=" * 80)
    
    # Puntuación de seguridad
    total_items = len(problemas) + len(advertencias) + len(correcto)
    score = (len(correcto) / total_items * 100) if total_items > 0 else 0
    
    print(f"\n[PUNTUACION] Seguridad: {score:.1f}%")
    
    if len(problemas) > 0:
        print("   [ADVERTENCIA] Hay problemas que deben resolverse")
    elif len(advertencias) > 0:
        print("   [ADVERTENCIA] Hay advertencias que deberian revisarse")
    else:
        print("   [OK] Configuracion de seguridad adecuada")

if __name__ == "__main__":
    verificar_seguridad()

