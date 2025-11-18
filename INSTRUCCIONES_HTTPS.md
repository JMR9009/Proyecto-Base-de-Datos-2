# ✅ HTTPS Configurado - Instrucciones de Uso

## 🎉 Estado: HTTPS Listo para Usar

He configurado HTTPS en tu proyecto. Aquí está lo que se hizo:

### ✅ Archivos Creados

1. **Certificados SSL generados:**
   - `certs/key.pem` - Clave privada
   - `certs/cert.pem` - Certificado SSL

2. **Scripts de inicio:**
   - `iniciar_servidor.py` - Detecta automáticamente HTTP o HTTPS
   - `iniciar_https.py` - Inicia solo con HTTPS
   - `generar_certificado_python.py` - Genera certificados con Python

3. **Configuración actualizada:**
   - `main.py` - CORS permite HTTPS
   - `vite.config.ts` - Proxy configurado para HTTPS
   - `middleware.py` - Ya detectaba HTTPS (sin cambios)

## 🚀 Cómo Usar HTTPS

### Opción 1: Inicio Automático (Recomendado)

```bash
cd Proyecto-Base-de-Datos-2
python iniciar_servidor.py
```

Este script:
- ✅ Detecta si hay certificados SSL
- ✅ Inicia con HTTPS si están disponibles
- ✅ Inicia con HTTP si no están disponibles

### Opción 2: Inicio Manual con HTTPS

```bash
cd Proyecto-Base-de-Datos-2
python iniciar_https.py
```

O con uvicorn directamente:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8443 \
    --ssl-keyfile certs/key.pem --ssl-certfile certs/cert.pem
```

## 📍 URLs Disponibles

### Con HTTPS (Recomendado)
- **Backend:** https://localhost:8443
- **Documentación:** https://localhost:8443/docs
- **Health Check:** https://localhost:8443/health

### Con HTTP (Alternativa)
- **Backend:** http://localhost:8000
- **Documentación:** http://localhost:8000/docs

## ⚠️ Advertencia del Navegador

Cuando accedas a `https://localhost:8443`, el navegador mostrará una advertencia porque el certificado es autofirmado. Esto es **normal en desarrollo**.

**Para aceptar:**
1. Haz clic en "Avanzado" o "Advanced"
2. Haz clic en "Continuar a localhost" o "Proceed to localhost"
3. El sitio funcionará normalmente

## 🔧 Configurar Frontend para HTTPS

### Opción 1: Usar Variable de Entorno

Crea un archivo `.env.local` en `frontend-citasmedicas/`:

```env
VITE_BACKEND_URL=https://127.0.0.1:8443
```

Luego reinicia el servidor de desarrollo del frontend.

### Opción 2: Actualizar vite.config.ts Manualmente

Edita `frontend-citasmedicas/vite.config.ts` y cambia:

```typescript
target: process.env.VITE_BACKEND_URL || 'https://127.0.0.1:8443',  // Cambiar a HTTPS
```

## ✅ Verificación

### 1. Verificar que el servidor está corriendo con HTTPS

```bash
curl -k https://localhost:8443/health
```

Deberías ver:
```json
{"status":"ok","message":"API funcionando correctamente"}
```

### 2. Verificar Headers de Seguridad

```bash
curl -kI https://localhost:8443/health | grep -i "strict-transport"
```

Deberías ver:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### 3. Verificar en el Navegador

1. Abre `https://localhost:8443/docs`
2. Verifica que aparece el candado 🔒 (después de aceptar la advertencia)
3. Abre DevTools → Network → Headers
4. Verifica que `Strict-Transport-Security` está presente

## 🔐 Seguridad Implementada

Con HTTPS ahora tienes:

- ✅ **Encriptación de datos** - Todo el tráfico está encriptado
- ✅ **Protección de tokens JWT** - Los tokens se transmiten de forma segura
- ✅ **Protección de contraseñas** - El login es seguro
- ✅ **HSTS activo** - Fuerza HTTPS siempre
- ✅ **Headers de seguridad** - Todos los headers activos

## 📝 Notas Importantes

1. **Certificados autofirmados**: Solo para desarrollo local
2. **Producción**: Usa Let's Encrypt con Nginx/Caddy (ver `GUIA_HTTPS_SEGURIDAD.md`)
3. **Puerto HTTPS**: 8443 (para evitar conflictos con HTTP en 8000)
4. **Middleware**: Detecta HTTPS automáticamente, no necesitas cambiar código

## 🎯 Próximos Pasos

1. ✅ HTTPS ya está configurado y funcionando
2. Inicia el servidor con `python iniciar_servidor.py`
3. Configura el frontend para usar HTTPS (ver arriba)
4. Prueba el login y verifica que funciona con HTTPS

## 🆘 Solución de Problemas

### Error: "Certificado no encontrado"
```bash
python generar_certificado_python.py
```

### Error: "Puerto 8443 en uso"
Cambia el puerto en `iniciar_https.py` o usa otro puerto.

### Frontend no se conecta
- Verifica que el backend está corriendo en HTTPS
- Verifica la configuración del proxy en `vite.config.ts`
- Revisa la consola del navegador para errores

## 📚 Documentación Adicional

- `GUIA_HTTPS_SEGURIDAD.md` - Guía completa de HTTPS
- `EJEMPLO_CONFIGURACION_HTTPS.md` - Ejemplos prácticos
- `README_HTTPS.md` - Guía rápida

---

**¡HTTPS está listo para usar!** 🎉

