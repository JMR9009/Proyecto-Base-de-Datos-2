# 🔧 Solución al Error de CORS

## ❌ Error Original
```
Access to XMLHttpRequest at 'http://127.0.0.1:8000/empleados/' (redirected from 'http://localhost:3001/api/empleados') 
from origin 'http://localhost:3001' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## ✅ Solución Aplicada

### 1. Actualizado CORS en `main.py`
Se agregaron los siguientes orígenes a `allow_origins`:
- `http://localhost:3001` ✅ (NUEVO)
- `http://127.0.0.1:3001` ✅ (NUEVO)
- `https://localhost:3001` ✅ (NUEVO)

### 2. Agregado método OPTIONS
Se agregó `OPTIONS` a `allow_methods` para permitir las peticiones preflight de CORS.

### 3. Actualizado puerto en `vite.config.ts`
Se cambió el puerto del servidor de desarrollo de `3000` a `3001` para coincidir con el puerto actual.

## 🔄 Pasos para Aplicar la Solución

### 1. Reiniciar el Servidor Backend
```bash
cd Proyecto-Base-de-Datos-2
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Verificar que el Frontend esté corriendo en el puerto 3001
Si el frontend no está corriendo, iniciarlo:
```bash
cd frontend-citasmedicas
npm run dev
```

### 3. Verificar la Conexión
- Abrir el navegador en `http://localhost:3001`
- Intentar hacer login o acceder a cualquier vista
- Verificar en la consola del navegador que no haya errores de CORS

## 📋 Configuración Actual de CORS

```python
allow_origins=[
    "http://localhost:3000", 
    "http://localhost:3001",  # ✅ NUEVO
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",  # ✅ NUEVO
    "http://127.0.0.1:5173",
    "https://localhost:3000",
    "https://localhost:3001",  # ✅ NUEVO
    "https://localhost:5173"
]
allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]  # ✅ OPTIONS agregado
```

## ⚠️ Notas Importantes

1. **El servidor backend DEBE reiniciarse** para que los cambios surtan efecto
2. Si el frontend está corriendo en otro puerto, agregarlo también a `allow_origins`
3. En producción, `allow_origins` debe contener solo los dominios permitidos (no usar `*`)

## 🐛 Si el Error Persiste

1. Verificar que el backend esté corriendo en `http://127.0.0.1:8000`
2. Verificar que el frontend esté corriendo en `http://localhost:3001`
3. Verificar en las DevTools del navegador (F12) la petición que falla
4. Verificar que el token JWT esté presente en el header `Authorization`
5. Revisar la consola del backend para ver si hay errores

