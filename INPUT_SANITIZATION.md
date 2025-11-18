# 🧹 Sanitización de Inputs - Guía Completa

## ¿Qué es Sanitizar Inputs?

**Sanitización** es el proceso de **limpiar y normalizar** los datos que ingresan a tu aplicación antes de procesarlos o almacenarlos. Es una medida de seguridad crítica que previene:

- ✅ **Inyección de código malicioso**
- ✅ **Ataques XSS (Cross-Site Scripting)**
- ✅ **Caracteres de control peligrosos**
- ✅ **Datos malformados**
- ✅ **Overflow de datos**

## 🔍 Diferencia: Validación vs Sanitización

### Validación
- **Qué hace**: Verifica que los datos cumplan ciertos criterios
- **Ejemplo**: "¿El email tiene formato válido?"
- **Resultado**: Acepta o rechaza el dato

### Sanitización
- **Qué hace**: Limpia y normaliza los datos
- **Ejemplo**: "Eliminar caracteres peligrosos del nombre"
- **Resultado**: Devuelve el dato limpio y seguro

**Ambas son necesarias**: Primero validas, luego sanitizas.

## 🛡️ Sanitización Implementada en Tu Código

### Función Principal: `sanitize_string()`

```python
def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitizar strings eliminando caracteres peligrosos"""
    if not isinstance(value, str):
        return ""
    # Eliminar caracteres de control y espacios al inicio/final
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value.strip())
    # Limitar longitud
    return sanitized[:max_length] if len(sanitized) > max_length else sanitized
```

### ¿Qué hace esta función?

1. **Verifica el tipo**: Asegura que sea un string
2. **Elimina espacios**: `strip()` elimina espacios al inicio y final
3. **Elimina caracteres de control**: 
   - `\x00-\x1f`: Caracteres de control ASCII (0-31)
   - `\x7f-\x9f`: Caracteres de control extendidos (127-159)
   - Estos incluyen: NULL, TAB, NEWLINE, etc.
4. **Limita longitud**: Previene overflow de datos

### Ejemplos de Caracteres Eliminados

```python
# Caracteres peligrosos que se eliminan:
- NULL (\x00)
- Tab (\x09)
- Newline (\x0a)
- Carriage Return (\x0d)
- Backspace (\x08)
- Delete (\x7f)
- Y otros caracteres de control
```

## 📋 Dónde se Usa la Sanitización

### 1. Modelos Pydantic (Validación Automática)

```python
class Medico(BaseModel):
    Nombre: str = Field(..., min_length=1, max_length=100)
    
    @validator('Nombre', 'Apellido', 'Especialidad')
    def sanitize_text(cls, v):
        return sanitize_string(v, max_length=100)  # ✅ Sanitiza automáticamente
```

**Flujo**:
1. Usuario envía: `"  Juan<script>alert('xss')</script>  "`
2. Validator sanitiza: `"Juan<script>alert('xss')</script>"`
3. Se almacena limpio en la BD

### 2. Campos Específicos

```python
@validator('Telefono')
def validate_phone(cls, v):
    v = sanitize_string(v, max_length=20)  # ✅ Primero sanitiza
    if not validate_phone(v):               # ✅ Luego valida
        raise ValueError('Formato de teléfono inválido')
    return v
```

## 🎯 Tipos de Sanitización Necesarios

### 1. Sanitización de Texto (Tu código actual)
✅ **Implementado**: Elimina caracteres de control y limita longitud

### 2. Sanitización HTML (Para prevenir XSS)
✅ **Implementado**: Funciones de escape HTML en backend y frontend
- Backend: `escape_html()` y `sanitize_html_input()` en `security.py`
- Frontend: `escapeHtml()` en `utils/security.ts`
- Componente Vue: `SafeText.vue` para renderizado seguro

### 3. Sanitización SQL (Para prevenir SQL Injection)
✅ **Implementado**: Usas parámetros preparados (`?`), no concatenación

### 4. Sanitización de URLs
⚠️ **No implementado**: Si aceptas URLs, valida formato

### 5. Sanitización de Números
✅ **Implementado**: Pydantic valida tipos automáticamente

## 🔒 Mejoras que Podrías Agregar

### 1. Escapar HTML (Si muestras datos en frontend)

```python
import html

def sanitize_html(value: str) -> str:
    """Escapar caracteres HTML para prevenir XSS"""
    return html.escape(value)
```

### 2. Normalizar Espacios Múltiples

```python
def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitizar strings eliminando caracteres peligrosos"""
    if not isinstance(value, str):
        return ""
    # Eliminar caracteres de control
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value.strip())
    # Normalizar espacios múltiples a uno solo
    sanitized = re.sub(r'\s+', ' ', sanitized)
    # Limitar longitud
    return sanitized[:max_length] if len(sanitized) > max_length else sanitized
```

### 3. Sanitización de Email (Ya validado, pero puedes normalizar)

```python
def sanitize_email(email: str) -> str:
    """Sanitizar email: lowercase y trim"""
    return email.strip().lower()
```

## 📊 Flujo Completo de Seguridad

```
Usuario envía datos
    ↓
1. Validación de tipo (Pydantic)
    ↓
2. Sanitización (sanitize_string)
    ↓
3. Validación de formato (validate_phone, validate_email)
    ↓
4. Validación de negocio (IDs existen, etc.)
    ↓
5. Almacenamiento seguro (parámetros preparados)
```

## ✅ Lo que Ya Tienes Implementado

- ✅ Sanitización de caracteres de control
- ✅ Limpieza de espacios
- ✅ Límite de longitud
- ✅ Validación de tipos
- ✅ Validación de formato
- ✅ Uso de parámetros preparados (SQL injection protegido)

## ⚠️ Lo que Podrías Mejorar

1. **Normalizar espacios múltiples**: `"Juan    Pérez"` → `"Juan Pérez"`
2. **Escapar HTML**: Si muestras datos en frontend HTML
3. **Normalizar emails**: Convertir a lowercase
4. **Sanitizar URLs**: Si aceptas URLs como input

## 🧪 Ejemplo Práctico

### Antes de Sanitización
```python
input_usuario = "  Juan<script>alert('xss')</script>  \x00Pérez  "
# Contiene:
# - Espacios al inicio/final
# - Código JavaScript malicioso
# - Carácter NULL peligroso
# - Espacios múltiples
```

### Después de Sanitización
```python
output = sanitize_string(input_usuario, max_length=100)
# Resultado: "Juan<script>alert('xss')</script>Pérez"
# Limpio pero aún tiene el script (necesitarías escapar HTML si lo muestras)
```

### Con Escapado HTML Adicional
```python
output_html = html.escape(output)
# Resultado: "Juan&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;Pérez"
# Ahora es seguro para mostrar en HTML
```

## 🎓 Resumen

**Sanitización** = Limpiar datos de entrada para hacerlos seguros

**Tu código actual**:
- ✅ Sanitiza caracteres de control
- ✅ Limpia espacios
- ✅ Limita longitud
- ✅ Valida formatos

**Recomendación**: Tu sanitización actual es buena para datos que se almacenan en BD. Si muestras datos en HTML, agrega escapado HTML.

