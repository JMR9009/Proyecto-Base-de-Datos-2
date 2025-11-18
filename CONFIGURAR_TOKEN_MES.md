# 📅 Configurar Token JWT para Durar 1 Mes

## ⏱️ Cálculo de Duración

**1 mes = 30 días = 720 horas = 43,200 minutos**

---

## 🔧 Método 1: Variable de Entorno (Recomendado)

### Paso 1: Crear archivo `.env`

Crea un archivo llamado `.env` en la carpeta `Proyecto-Base-de-Datos-2/`:

```env
ACCESS_TOKEN_EXPIRE_MINUTES=43200
SECRET_KEY=tu-clave-secreta-super-segura-cambiar-en-produccion
ALGORITHM=HS256
ENVIRONMENT=development
```

### Paso 2: Instalar python-dotenv (si no lo tienes)

```bash
pip install python-dotenv
```

### Paso 3: Cargar variables de entorno en `main.py`

Agrega al inicio de `main.py`:

```python
from dotenv import load_dotenv
load_dotenv()  # Carga variables del archivo .env
```

### Paso 4: Reiniciar el servidor

```bash
python -m uvicorn main:app --reload --port 8000
```

---

## 🔧 Método 2: Modificar Código Directamente

### Editar `auth.py`

Abre `Proyecto-Base-de-Datos-2/auth.py` y busca la línea 19:

**Antes**:
```python
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "3600"))
```

**Después**:
```python
# Duración del token: 1 mes = 30 días = 43,200 minutos
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))
```

### Reiniciar el servidor

```bash
python -m uvicorn main:app --reload --port 8000
```

---

## 🔧 Método 3: Variable de Entorno del Sistema

### Windows (PowerShell)

```powershell
# Temporal (solo para esta sesión)
$env:ACCESS_TOKEN_EXPIRE_MINUTES="43200"

# Permanente (para el usuario)
[System.Environment]::SetEnvironmentVariable("ACCESS_TOKEN_EXPIRE_MINUTES", "43200", "User")
```

### Windows (CMD)

```cmd
setx ACCESS_TOKEN_EXPIRE_MINUTES "43200"
```

### Linux/Mac

```bash
# Temporal
export ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Permanente (agregar al ~/.bashrc o ~/.zshrc)
echo 'export ACCESS_TOKEN_EXPIRE_MINUTES=43200' >> ~/.bashrc
source ~/.bashrc
```

---

## ✅ Verificar que Funciona

### Opción 1: Verificar en el código

Crea un archivo `verificar_token_expiration.py`:

```python
from auth import ACCESS_TOKEN_EXPIRE_MINUTES

print(f"✅ Duración configurada: {ACCESS_TOKEN_EXPIRE_MINUTES} minutos")
print(f"   Equivalente a: {ACCESS_TOKEN_EXPIRE_MINUTES / 60} horas")
print(f"   Equivalente a: {ACCESS_TOKEN_EXPIRE_MINUTES / 1440} días")
print(f"   Equivalente a: {ACCESS_TOKEN_EXPIRE_MINUTES / 43200} meses")
```

Ejecuta:
```bash
python verificar_token_expiration.py
```

**Resultado esperado**:
```
✅ Duración configurada: 43200 minutos
   Equivalente a: 720.0 horas
   Equivalente a: 30.0 días
   Equivalente a: 1.0 meses
```

### Opción 2: Probar con un login

1. Haz login en tu aplicación
2. Copia el token recibido
3. Ve a [jwt.io](https://jwt.io)
4. Pega el token y decodifícalo
5. Verifica el campo `exp` (expiration)
6. Calcula la diferencia con `iat` (issued at)

**Ejemplo**:
```json
{
  "sub": "1",
  "iat": 1704067200,  // 1 de enero 2024
  "exp": 1706659200   // 31 de enero 2024 (30 días después)
}
```

---

## 📊 Tabla de Conversión

| Duración | Minutos | Horas | Días |
|----------|---------|-------|------|
| 1 hora | 60 | 1 | 0.04 |
| 1 día | 1,440 | 24 | 1 |
| 1 semana | 10,080 | 168 | 7 |
| **1 mes** | **43,200** | **720** | **30** |
| 3 meses | 129,600 | 2,160 | 90 |
| 1 año | 525,600 | 8,760 | 365 |

---

## ⚠️ Consideraciones de Seguridad

### Tokens de 1 Mes

✅ **Ventajas**:
- Excelente experiencia de usuario
- No requiere login frecuente
- Ideal para aplicaciones móviles

❌ **Desventajas**:
- Mayor riesgo si el token es robado
- Token válido por mucho tiempo
- Más difícil revocar acceso

### Recomendaciones:

1. **Usar HTTPS siempre** - Los tokens deben transmitirse solo sobre HTTPS
2. **Implementar refresh tokens** - Para mejor seguridad:
   - Access token: 15-30 minutos (corto)
   - Refresh token: 30 días (largo)
3. **Logout forzado** - Implementar endpoint para invalidar tokens
4. **Monitoreo** - Detectar uso anormal de tokens

---

## 🔄 Después de Cambiar la Configuración

1. **Reiniciar el servidor** - Los cambios solo aplican a tokens nuevos
2. **Los tokens antiguos** - Mantendrán su duración original
3. **Nuevos logins** - Usarán la nueva duración

---

## 📝 Resumen Rápido

**Para que dure 1 mes**:

1. **Opción más fácil**: Edita `auth.py` línea 19:
   ```python
   ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))
   ```

2. **Opción recomendada**: Crea archivo `.env`:
   ```env
   ACCESS_TOKEN_EXPIRE_MINUTES=43200
   ```

3. **Reinicia el servidor**

4. **Verifica** con un nuevo login

---

## 🎯 Resultado

Después de configurar, los tokens JWT durarán **30 días** (1 mes) desde el momento del login.

