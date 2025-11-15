import pyodbc
from config import settings
from typing import Optional


class Database:
    """Clase para gestionar conexiones a la base de datos"""
    
    @staticmethod
    def get_connection():
        """Obtiene una conexión a la base de datos"""
        try:
            return pyodbc.connect(settings.connection_string)
        except pyodbc.Error as e:
            raise ConnectionError(f"Error al conectar con la base de datos: {str(e)}")
    
    @staticmethod
    def execute_query(query: str, params: Optional[tuple] = None):
        """Ejecuta una consulta SELECT y retorna los resultados"""
        conn = None
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def execute_update(query: str, params: Optional[tuple] = None):
        """Ejecuta una consulta INSERT, UPDATE o DELETE"""
        conn = None
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.rowcount
        except pyodbc.Error as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
