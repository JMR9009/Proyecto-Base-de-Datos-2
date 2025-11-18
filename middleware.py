"""
Middleware de seguridad para la API
"""
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import os
from collections import defaultdict
from typing import Dict, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Rate limiting: almacenar requests por IP
rate_limit_store: Dict[str, list] = defaultdict(list)
RATE_LIMIT_REQUESTS = 100  # Número de requests permitidos
RATE_LIMIT_WINDOW = 60  # Ventana de tiempo en segundos


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware para agregar headers de seguridad HTTP"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Detectar si se usa HTTPS
        is_https = request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https"
        is_production = os.getenv("ENVIRONMENT", "development").lower() == "production"
        
        # Headers de seguridad básicos (siempre)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS solo en HTTPS o producción (preparado para HTTPS)
        if is_https or is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Remover header que expone información del servidor
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware para limitar la tasa de requests por IP"""
    
    async def dispatch(self, request: Request, call_next):
        # Obtener IP del cliente
        client_ip = request.client.host if request.client else "unknown"
        
        # Limpiar requests antiguos
        current_time = time.time()
        rate_limit_store[client_ip] = [
            req_time for req_time in rate_limit_store[client_ip]
            if current_time - req_time < RATE_LIMIT_WINDOW
        ]
        
        # Verificar límite
        if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
            logger.warning(f"Rate limit excedido para IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Demasiadas solicitudes",
                    "message": f"Límite de {RATE_LIMIT_REQUESTS} requests por {RATE_LIMIT_WINDOW} segundos excedido"
                }
            )
        
        # Registrar request
        rate_limit_store[client_ip].append(current_time)
        
        # Agregar headers de rate limit
        remaining = RATE_LIMIT_REQUESTS - len(rate_limit_store[client_ip])
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + RATE_LIMIT_WINDOW))
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para registrar todas las requests"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Obtener información de la request
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Procesar request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log solo requests importantes o con errores
            if response.status_code >= 400 or process_time > 1.0:
                logger.info(
                    f"{method} {path} - Status: {response.status_code} - "
                    f"IP: {client_ip} - Time: {process_time:.3f}s"
                )
            
            # Agregar tiempo de procesamiento al header
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error en {method} {path} - IP: {client_ip} - "
                f"Time: {process_time:.3f}s - Error: {str(e)}",
                exc_info=True
            )
            raise


class PayloadSizeMiddleware(BaseHTTPMiddleware):
    """Middleware para limitar el tamaño del payload"""
    
    MAX_PAYLOAD_SIZE = 1024 * 1024  # 1MB
    
    async def dispatch(self, request: Request, call_next):
        # Verificar tamaño del body solo para métodos que lo tienen
        if request.method in ["POST", "PUT", "PATCH"]:
            content_length = request.headers.get("content-length")
            if content_length:
                try:
                    size = int(content_length)
                    if size > self.MAX_PAYLOAD_SIZE:
                        logger.warning(
                            f"Payload demasiado grande: {size} bytes desde IP: {request.client.host}"
                        )
                        return JSONResponse(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            content={
                                "error": "Payload demasiado grande",
                                "message": f"El tamaño máximo permitido es {self.MAX_PAYLOAD_SIZE} bytes"
                            }
                        )
                except ValueError:
                    pass
        
        return await call_next(request)


class ContentTypeValidationMiddleware(BaseHTTPMiddleware):
    """Middleware para validar Content-Type en requests con body"""
    
    async def dispatch(self, request: Request, call_next):
        # Solo validar para métodos que tienen body
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            
            # Permitir JSON y form-data
            if not (content_type.startswith("application/json") or 
                   content_type.startswith("multipart/form-data") or
                   content_type.startswith("application/x-www-form-urlencoded")):
                return JSONResponse(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    content={
                        "error": "Content-Type no soportado",
                        "message": "Se requiere application/json"
                    }
                )
        
        return await call_next(request)

