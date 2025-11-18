"""
Módulo de seguridad para la aplicación
"""
import re
from typing import Optional
from pydantic import BaseModel, EmailStr, validator, Field
from datetime import datetime

# Expresiones regulares para validación
PHONE_PATTERN = re.compile(r'^\+?[\d\s\-\(\)]{8,15}$')
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')

def sanitize_string(value: str, max_length: int = 255) -> str:
    """
    Sanitizar strings eliminando caracteres peligrosos y normalizando.
    
    Proceso:
    1. Elimina espacios al inicio y final
    2. Elimina caracteres de control peligrosos (NULL, TAB, etc.)
    3. Normaliza espacios múltiples a uno solo
    4. Limita la longitud máxima
    
    Args:
        value: String a sanitizar
        max_length: Longitud máxima permitida (default: 255)
    
    Returns:
        String sanitizado y seguro para almacenar
    """
    if not isinstance(value, str):
        return ""
    
    # Paso 1: Eliminar espacios al inicio y final
    sanitized = value.strip()
    
    # Paso 2: Eliminar caracteres de control peligrosos
    # \x00-\x1f: Caracteres de control ASCII (NULL, TAB, NEWLINE, etc.)
    # \x7f-\x9f: Caracteres de control extendidos (DELETE, etc.)
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Paso 3: Normalizar espacios múltiples a uno solo
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    # Paso 4: Limitar longitud
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized

def validate_email(email: str) -> bool:
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validar formato de teléfono"""
    return bool(PHONE_PATTERN.match(phone))

def validate_date(date_string: str) -> bool:
    """Validar formato de fecha YYYY-MM-DD"""
    if not DATE_PATTERN.match(date_string):
        return False
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def escape_html(text: str) -> str:
    """
    Escapar caracteres HTML para prevenir XSS (Cross-Site Scripting).
    
    Convierte caracteres HTML especiales a sus entidades HTML:
    - < → &lt;
    - > → &gt;
    - & → &amp;
    - " → &quot;
    - ' → &#x27;
    
    Args:
        text: Texto que puede contener HTML
    
    Returns:
        Texto con caracteres HTML escapados, seguro para mostrar en HTML
    
    Ejemplo:
        escape_html("<script>alert('xss')</script>")
        # Retorna: "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
    """
    if not isinstance(text, str):
        return ""
    
    # Mapeo de caracteres HTML peligrosos a entidades HTML
    html_escape_map = {
        '&': '&amp;',   # Debe ir primero para no escapar otros escapes
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',  # También se puede usar &#39;
    }
    
    escaped = text
    for char, entity in html_escape_map.items():
        escaped = escaped.replace(char, entity)
    
    return escaped


def sanitize_html_input(value: str, max_length: int = 255) -> str:
    """
    Sanitizar input que puede contener HTML: primero sanitiza, luego escapa HTML.
    
    Útil para campos de texto que se mostrarán en HTML pero no deben contener código.
    
    Args:
        value: String que puede contener HTML malicioso
        max_length: Longitud máxima permitida
    
    Returns:
        String sanitizado y con HTML escapado, seguro para mostrar
    """
    # Primero sanitizar (eliminar caracteres de control, normalizar)
    sanitized = sanitize_string(value, max_length)
    # Luego escapar HTML
    return escape_html(sanitized)


def safe_error_message(error: Exception, is_production: bool = False) -> str:
    """Retornar mensaje de error seguro sin exponer detalles internos"""
    if is_production:
        return "Error interno del servidor. Por favor, contacte al administrador."
    return str(error)

