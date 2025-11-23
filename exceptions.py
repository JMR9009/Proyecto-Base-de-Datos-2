from fastapi import HTTPException, status


class DatabaseError(HTTPException):
    """Excepción personalizada para errores de base de datos"""
    def __init__(self, detail: str = "Error en la base de datos"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class NotFoundError(HTTPException):
    """Excepción personalizada para recursos no encontrados"""
    def __init__(self, resource: str, resource_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} con ID {resource_id} no encontrado"
        )


class ValidationError(HTTPException):
    """Excepción personalizada para errores de validación"""
    def __init__(self, detail: str = "Error de validación"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


