import os
from typing import Optional


class Settings:
    """Configuración de la aplicación"""
    
    # Base de datos
    DB_DRIVER: str = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    DB_SERVER: str = os.getenv("DB_SERVER", "MANUEL\\MSSQL2022")
    DB_DATABASE: str = os.getenv("DB_DATABASE", "ClinicaMedica")
    DB_USER: Optional[str] = os.getenv("DB_USER", None)
    DB_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD", None)
    DB_TRUSTED_CONNECTION: str = os.getenv("DB_TRUSTED_CONNECTION", "yes")
    
    # API
    API_TITLE: str = "API Clínica Médica"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API para gestión de pacientes, médicos y citas"
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    @property
    def connection_string(self) -> str:
        """Genera la cadena de conexión a la base de datos"""
        if self.DB_TRUSTED_CONNECTION.lower() == "yes":
            return (
                f"DRIVER={{{self.DB_DRIVER}}};"
                f"SERVER={self.DB_SERVER};"
                f"DATABASE={self.DB_DATABASE};"
                f"Trusted_Connection=yes;"
            )
        else:
            return (
                f"DRIVER={{{self.DB_DRIVER}}};"
                f"SERVER={self.DB_SERVER};"
                f"DATABASE={self.DB_DATABASE};"
                f"UID={self.DB_USER};"
                f"PWD={self.DB_PASSWORD};"
            )


settings = Settings()

