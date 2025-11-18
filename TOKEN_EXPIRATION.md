# ⏱️ Duración de Tokens JWT

## 📊 Configuración Actual

### Duración del Token de Acceso

**Valor por defecto**: **3600 minutos** (60 horas)

**Ubicación**: `auth.py` línea 19

```python
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "3600"))
```

### Conversión de Tiempo

| Unidad | Valor |
|--------|-------|
| **Minutos** | 3600 minutos |
| **Horas** | 60 horas |
| **Días** | 2.5 días |

---

## 🔧 Cómo Cambiar la Duración

### Opción 1: Variable de Entorno (Recomendado)

Crea un archivo `.env` en la raíz del proyecto:

```env
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

O configura la variable de entorno en tu sistema:

**Windows (PowerShell)**:
```powershell
$env:ACCESS_TOKEN_EXPIRE_MINUTES="30"
```

**Linux/Mac**:
```bash
export ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Opción 2: Modificar el Código

Edita `auth.py` línea 19:

```python
# Para 30 minutos
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Para 1 hora
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Para 24 horas
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
```

---

## 📋 Valores Recomendados por Tipo de Aplicación

### Desarrollo
- **30 minutos** - Para pruebas rápidas
- **60 minutos** - Valor común para desarrollo

### Producción - Aplicaciones Web
- **15-30 minutos** - Máxima seguridad
- **60 minutos** - Balance entre seguridad y UX
- **120 minutos** - Para aplicaciones internas

### Producción - Aplicaciones Móviles
- **24 horas** - Mejor experiencia de usuario
- **7 días** - Con refresh tokens

---

## 🔍 Verificar la Duración Actual

### Método 1: Verificar en el Código

```python
from auth import ACCESS_TOKEN_EXPIRE_MINUTES
print(f"Los tokens duran {ACCESS_TOKEN_EXPIRE_MINUTES} minutos")
print(f"Equivalente a {ACCESS_TOKEN_EXPIRE_MINUTES / 60} horas")
```

### Método 2: Decodificar un Token

Los tokens JWT contienen el campo `exp` (expiration) que indica cuándo expiran.

Puedes decodificar un token en [jwt.io](https://jwt.io) para ver:
- `exp`: Timestamp de expiración
- `iat`: Timestamp de creación

**Ejemplo**:
```json
{
  "sub": "1",
  "exp": 1763486134,  // Timestamp Unix
  "iat": 1763484334   // Timestamp Unix
}
```

---

## ⚠️ Consideraciones de Seguridad

### Tokens de Corta Duración (15-30 min)
✅ **Ventajas**:
- Mayor seguridad
- Menor riesgo si el token es robado
- Cumple con mejores prácticas

❌ **Desventajas**:
- Usuario debe hacer login más frecuentemente
- Peor experiencia de usuario

### Tokens de Larga Duración (24+ horas)
✅ **Ventajas**:
- Mejor experiencia de usuario
- Menos interrupciones

❌ **Desventajas**:
- Mayor riesgo si el token es robado
- Token válido por mucho tiempo

### Recomendación: Refresh Tokens

Para mejor seguridad y UX, implementa:
- **Access Token**: 15-30 minutos (corto)
- **Refresh Token**: 7-30 días (largo)

El refresh token se usa para obtener un nuevo access token sin hacer login.

---

## 🔄 Implementación Actual

### Cómo Funciona

1. Usuario hace login → Recibe token
2. Token válido por **3600 minutos** (60 horas)
3. Después de ese tiempo → Token expira
4. Usuario debe hacer login nuevamente

### Código Relevante

```python
# auth.py - create_access_token()
if expires_delta:
    expire = datetime.utcnow() + expires_delta
else:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
```

---

## 📝 Resumen

**Duración Actual**: **3600 minutos** (60 horas / 2.5 días)

**Para cambiar**:
1. Configura variable de entorno `ACCESS_TOKEN_EXPIRE_MINUTES`
2. O modifica el valor por defecto en `auth.py`

**Recomendación**: 
- Desarrollo: 30-60 minutos
- Producción: 15-30 minutos (con refresh tokens)

