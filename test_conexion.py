import pyodbc
from config import settings

print('='*60)
print('PRUEBA DE CONEXION A SQL SERVER')
print('='*60)
print()
print('Configuración:')
print(f'  Servidor: {settings.DB_SERVER}')
print(f'  Base de Datos: {settings.DB_DATABASE}')
print(f'  Usuario: {settings.DB_USER}')
print(f'  Driver: {settings.DB_DRIVER}')
print()

try:
    print('Intentando conectar...')
    conn = pyodbc.connect(settings.connection_string)
    cursor = conn.cursor()
    
    print('✅ CONEXION EXITOSA')
    print()
    
    # Verificar tablas
    cursor.execute("""
        SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """)
    
    tables = cursor.fetchall()
    print(f'Tablas en la base de datos ({len(tables)}):')
    for table in tables:
        print(f'  • {table[0]}')
    
    conn.close()
    print()
    print('='*60)
    print('✅ CONEXION VERIFICADA')
    print('='*60)
    
except pyodbc.Error as e:
    print(f'❌ ERROR DE CONEXION')
    print(f'Detalle: {str(e)}')
except Exception as e:
    print(f'❌ ERROR: {str(e)}')
