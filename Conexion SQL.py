"""
Script de prueba de conexión a SQL Server
Verifica la conexión y muestra la versión del servidor
"""
import pyodbc
import logging
from config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_connection():
    """Prueba la conexión a la base de datos y muestra la versión del servidor"""
    connection = None
    cursor = None
    
    try:
        # Usar configuración centralizada
        connection = pyodbc.connect(settings.connection_string)
        logger.info('Conexión exitosa a la base de datos')
        
        cursor = connection.cursor()
        cursor.execute('SELECT @@version;')
        row = cursor.fetchone()
        
        if row:
            logger.info(f'Versión del servidor SQL: {row[0]}')
            return True
        else:
            logger.warning('No se pudo obtener la versión del servidor')
            return False
            
    except pyodbc.Error as e:
        logger.error(f'Error de base de datos: {e}')
        return False
    except Exception as e:
        logger.error(f'Error inesperado: {e}')
        return False
    finally:
        # Cerrar cursor y conexión de forma segura
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            logger.info('Conexión cerrada correctamente')


if __name__ == '__main__':
    """Ejecutar prueba de conexión si se ejecuta directamente"""
    success = test_connection()
    exit(0 if success else 1)
