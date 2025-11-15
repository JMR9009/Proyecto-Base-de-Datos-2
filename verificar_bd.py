from config import settings
import pyodbc

print('='*70)
print('VERIFICACION DE CONEXION A BASE DE DATOS')
print('='*70)
print()

print('Configuración en .env:')
print(f'  Servidor: {settings.DB_SERVER}')
print(f'  Base de Datos: {settings.DB_DATABASE}')
print(f'  Usuario: {settings.DB_USER}')
print(f'  Driver: {settings.DB_DRIVER}')
print(f'  Trusted Connection: {settings.DB_TRUSTED_CONNECTION}')
print()

try:
    print('Conectando...')
    conn = pyodbc.connect(settings.connection_string)
    cursor = conn.cursor()
    
    # Obtener nombre actual de BD
    cursor.execute('SELECT DB_NAME() as base_datos_actual')
    bd_actual = cursor.fetchone()[0]
    
    # Obtener usuario actual
    cursor.execute('SELECT CURRENT_USER as usuario_actual')
    usuario_actual = cursor.fetchone()[0]
    
    print()
    print('='*70)
    print('✅ CONEXION EXITOSA')
    print('='*70)
    print()
    print(f'Base de Datos Actual: {bd_actual}')
    print(f'Usuario Conectado: {usuario_actual}')
    print()
    
    # Listar tablas
    cursor.execute("""
        SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE' 
        ORDER BY TABLE_NAME
    """)
    
    tables = cursor.fetchall()
    print(f'Tablas en la BD ({len(tables)}):')
    for table in tables:
        print(f'  • {table[0]}')
    
    conn.close()
    
except pyodbc.Error as e:
    print(f'❌ ERROR: {str(e)}')
