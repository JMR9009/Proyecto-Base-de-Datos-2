# 🛡️ Protección contra XSS (Cross-Site Scripting)

## ✅ Implementación Completa

La protección contra XSS está implementada en **ambos lados**: Backend y Frontend.

## 🔒 Backend (Python/FastAPI)

### Funciones Disponibles

#### 1. `escape_html(text: str) -> str`
Escapa caracteres HTML peligrosos para prevenir XSS.

```python
from security import escape_html

# Ejemplo
input_malicioso = "<script>alert('xss')</script>"
safe_output = escape_html(input_malicioso)
# Resultado: "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
```

**Caracteres escapados**:
- `<` → `&lt;`
- `>` → `&gt;`
- `&` → `&amp;`
- `"` → `&quot;`
- `'` → `&#x27;`

#### 2. `sanitize_html_input(value: str, max_length: int = 255) -> str`
Combina sanitización y escape HTML.

```python
from security import sanitize_html_input

# Primero sanitiza (elimina caracteres de control, normaliza)
# Luego escapa HTML
safe_text = sanitize_html_input(user_input, max_length=500)
```

### Uso en Modelos

Los campos que se mostrarán en HTML usan `sanitize_html_input`:

```python
# En models/cita.py
@validator('Motivo')
def sanitize_motivo(cls, v):
    # Sanitiza Y escapa HTML
    return sanitize_html_input(v, max_length=500)
```

## 🎨 Frontend (Vue.js/TypeScript)

### Funciones Disponibles

#### 1. `escapeHtml(text: string): string`
Escapa caracteres HTML en TypeScript.

```typescript
import { escapeHtml } from '@/utils/security'

const userInput = "<script>alert('xss')</script>"
const safe = escapeHtml(userInput)
// Resultado: "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
```

#### 2. Componente `SafeText`
Componente Vue para mostrar texto de forma segura.

```vue
<template>
  <SafeText :text="paciente.Nombre" />
</template>

<script setup lang="ts">
import SafeText from '@/components/SafeText.vue'
</script>
```

### Protección Automática de Vue

**Vue.js escapa automáticamente** el contenido en interpolaciones `{{ }}`:

```vue
<!-- ✅ SEGURO - Vue escapa automáticamente -->
<div>{{ paciente.Nombre }}</div>

<!-- ❌ PELIGROSO - NUNCA usar v-html con datos del usuario -->
<div v-html="userInput"></div>
```

## 🔄 Flujo Completo de Protección

```
Usuario envía: "<script>alert('xss')</script>"
    ↓
1. Frontend: Sanitiza antes de enviar (opcional, capa adicional)
    ↓
2. Backend: Recibe y valida con Pydantic
    ↓
3. Backend: Sanitiza con sanitize_string()
    ↓
4. Backend: Escapa HTML con escape_html() (si se mostrará en HTML)
    ↓
5. Backend: Almacena en BD (limpio y escapado)
    ↓
6. Frontend: Recibe datos del backend
    ↓
7. Frontend: Vue escapa automáticamente en {{ }}
    ↓
8. Frontend: Opcionalmente usa escapeHtml() para más control
    ↓
Resultado: Texto completamente seguro para mostrar
```

## 📋 Dónde se Aplica

### Backend - Campos que se Escapan

- ✅ `Cita.Motivo` - Se muestra en tablas y formularios
- ✅ `Cita.Estado` - Se muestra en la UI
- ⚠️ Otros campos usan solo `sanitize_string()` (suficiente si Vue escapa)

### Frontend - Protección Automática

- ✅ Vue escapa automáticamente en `{{ }}`
- ✅ Element Plus escapa en `el-table-column prop`
- ✅ Componente `SafeText` disponible para casos especiales

## 🧪 Ejemplo de Ataque Prevenido

### Sin Protección (Peligroso)
```html
<!-- Usuario envía: -->
Nombre: "<img src=x onerror=alert('XSS')>"

<!-- Sin escape, se ejecuta el JavaScript -->
<div>{{ nombre }}</div>
<!-- Resultado: Se ejecuta alert('XSS') -->
```

### Con Protección (Seguro)
```html
<!-- Usuario envía: -->
Nombre: "<img src=x onerror=alert('XSS')>"

<!-- Backend escapa: -->
Nombre: "&lt;img src=x onerror=alert(&#x27;XSS&#x27;)&gt;"

<!-- Vue muestra como texto: -->
<div>{{ nombre }}</div>
<!-- Resultado: Se muestra como texto, NO se ejecuta -->
```

## ✅ Checklist Completo de Protección XSS

### 🔒 Backend (Python/FastAPI)
- [x] **Escape HTML** - `escape_html()` implementada en `security.py`
- [x] **Sanitización HTML** - `sanitize_html_input()` implementada
- [x] **Sanitización básica** - `sanitize_string()` en todos los campos de texto
- [x] **Validación Pydantic** - Todos los modelos validan y sanitizan
- [x] **Campos críticos** - `Cita.Motivo` y `Cita.Estado` usan `sanitize_html_input()`
- [x] **Parámetros preparados** - SQL injection protegido con `?`

### 🎨 Frontend (Vue.js/TypeScript)
- [x] **Escape HTML** - `escapeHtml()` implementada en `utils/security.ts`
- [x] **Sanitización** - `sanitizeString()` disponible
- [x] **Componente SafeText** - `SafeText.vue` creado
- [x] **Vue auto-escape** - Escapa automáticamente en `{{ }}` y `prop`
- [x] **NO v-html peligroso** - Verificado, no se usa `v-html` con datos del usuario
- [x] **Todas las vistas** - PacientesView, MedicosView, CitasView protegidas

### 📚 Documentación
- [x] **XSS_PROTECTION.md** - Documentación completa
- [x] **INPUT_SANITIZATION.md** - Guía de sanitización
- [x] **XSS_CHECKLIST.md** - Checklist detallado
- [x] **README_SECURITY.md** (Frontend) - Guía de uso

### 🧪 Verificación
- [x] **Test script** - `test_sanitization.py` disponible
- [x] **Sin v-html** - Verificado con grep
- [x] **Campos protegidos** - Todos los campos de texto sanitizados

## 🎯 Buenas Prácticas

1. **NUNCA usar `v-html`** con datos del usuario sin sanitizar
2. **Confiar en Vue** - escapa automáticamente en `{{ }}`
3. **Sanitizar en backend** - primera línea de defensa
4. **Escapar HTML** - para campos que se muestran directamente
5. **Validar en ambos lados** - frontend y backend

## 📚 Archivos Relacionados

### Backend
- `security.py` - Funciones `escape_html()` y `sanitize_html_input()`
- `models/cita.py` - Uso de `sanitize_html_input()` en validators

### Frontend
- `src/utils/security.ts` - Funciones de escape HTML
- `src/utils/safeRender.ts` - Componentes y directivas seguras
- `src/components/SafeText.vue` - Componente para renderizado seguro
- `src/utils/README_SECURITY.md` - Guía de uso

## 🔍 Verificación

Para verificar que la protección funciona:

1. Intenta crear un paciente con: `<script>alert('xss')</script>`
2. El backend lo sanitiza y escapa
3. Vue lo muestra como texto, NO como código ejecutable
4. El ataque XSS está prevenido ✅

## 🎓 Resumen

**Protección XSS**: ✅ **Implementada completamente**

- Backend: Escape HTML automático en campos críticos
- Frontend: Vue escapa automáticamente + funciones adicionales
- Componentes: SafeText disponible para casos especiales
- Documentación: Guías y ejemplos disponibles

