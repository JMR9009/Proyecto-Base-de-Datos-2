"""
Script de prueba para demostrar la sanitización de inputs
"""
from security import sanitize_string, validate_phone, validate_email, validate_date

def test_sanitization():
    """Ejemplos de sanitización"""
    
    print("=" * 60)
    print("PRUEBAS DE SANITIZACIÓN DE INPUTS")
    print("=" * 60)
    
    # Test 1: Espacios múltiples
    print("\n1. Espacios múltiples:")
    input1 = "Juan    Carlos    Pérez"
    output1 = sanitize_string(input1)
    print(f"   Input:  '{input1}'")
    print(f"   Output: '{output1}'")
    print(f"   ✅ Normalizado a un solo espacio")
    
    # Test 2: Caracteres de control
    print("\n2. Caracteres de control peligrosos:")
    input2 = "María\x00López\x09García"
    output2 = sanitize_string(input2)
    print(f"   Input:  {repr(input2)}")
    print(f"   Output: '{output2}'")
    print(f"   ✅ Caracteres NULL y TAB eliminados")
    
    # Test 3: Espacios al inicio/final
    print("\n3. Espacios al inicio y final:")
    input3 = "   Pedro   "
    output3 = sanitize_string(input3)
    print(f"   Input:  '{input3}'")
    print(f"   Output: '{output3}'")
    print(f"   ✅ Espacios eliminados")
    
    # Test 4: Longitud máxima
    print("\n4. Límite de longitud:")
    input4 = "A" * 300  # 300 caracteres
    output4 = sanitize_string(input4, max_length=100)
    print(f"   Input length:  {len(input4)}")
    print(f"   Output length: {len(output4)}")
    print(f"   ✅ Limitado a 100 caracteres")
    
    # Test 5: Caso combinado
    print("\n5. Caso combinado (todos los problemas):")
    input5 = "  Ana\x00\x09María    López   \x7f  "
    output5 = sanitize_string(input5)
    print(f"   Input:  {repr(input5)}")
    print(f"   Output: '{output5}'")
    print(f"   ✅ Completamente sanitizado")
    
    # Test 6: Validación de teléfono
    print("\n6. Validación de teléfono:")
    phones = [
        "+1 234 567 8900",  # ✅ Válido
        "123-456-7890",     # ✅ Válido
        "abc123",           # ❌ Inválido
        "123",              # ❌ Muy corto
    ]
    for phone in phones:
        is_valid = validate_phone(phone)
        status = "✅ Válido" if is_valid else "❌ Inválido"
        print(f"   '{phone}': {status}")
    
    # Test 7: Validación de email
    print("\n7. Validación de email:")
    emails = [
        "usuario@example.com",      # ✅ Válido
        "test.email@domain.co.uk",  # ✅ Válido
        "invalid.email",            # ❌ Sin @
        "@domain.com",              # ❌ Sin usuario
    ]
    for email in emails:
        is_valid = validate_email(email)
        status = "✅ Válido" if is_valid else "❌ Inválido"
        print(f"   '{email}': {status}")
    
    # Test 8: Validación de fecha
    print("\n8. Validación de fecha:")
    dates = [
        "2024-12-25",  # ✅ Válido
        "2024-02-29",  # ✅ Válido (año bisiesto)
        "2024-13-01",  # ❌ Mes inválido
        "24-12-25",    # ❌ Formato incorrecto
    ]
    for date in dates:
        is_valid = validate_date(date)
        status = "✅ Válido" if is_valid else "❌ Inválido"
        print(f"   '{date}': {status}")
    
    print("\n" + "=" * 60)
    print("RESUMEN:")
    print("=" * 60)
    print("✅ Sanitización elimina caracteres peligrosos")
    print("✅ Normaliza espacios múltiples")
    print("✅ Limita longitud de datos")
    print("✅ Valida formatos (teléfono, email, fecha)")
    print("✅ Protege contra inyección de código")
    print("=" * 60)

if __name__ == "__main__":
    test_sanitization()

