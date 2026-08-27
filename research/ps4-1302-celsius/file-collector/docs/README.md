# PS4 userland file collector — protocolo seguro

Este directorio contiene un recolector **consent-only** y un servidor receptor para Android/Termux. El servidor recibe archivos que el operador haya incluido explícitamente en un manifiesto; no navega el sistema remoto, no lee la PS4 por sí mismo y no ejecuta archivos recibidos.

## Componentes

| Archivo | Función |
|---|---|
| `termux-server/server.py` | Servidor HTTP receptor. Expone sólo `/v1/manifest`, `/v1/status`, `/v1/chunk` y `/v1/finalize`, protegido por Bearer token. |
| `ps4-client/userland_collector.js` | Adaptador JavaScript. Requiere que el caller proporcione un `readChunk` explícito; no incluye una primitiva de WebKit ni un lector nativo. |
| `config/manifest.example.json` | Ejemplo de allowlist. Por defecto se limita a `/mnt/usb0/RESEARCH/`. |

## Protocolo

El operador prepara un manifiesto con un `id`, una ruta de origen autorizada, un destino relativo, tamaño y SHA-256 esperado. El cliente obtiene el estado, lee bloques de hasta 1 MiB, calcula SHA-256 por bloque, reintenta errores de red y continúa desde el último offset registrado. El servidor guarda cada bloque en `.parts/`, rechaza IDs no incluidos, valida límites y hash de cada bloque, reconstruye en orden y sólo publica el archivo final después de validar tamaño y SHA-256 total.

No existe endpoint de listado arbitrario. No se aceptan rutas con `..` o destinos absolutos. El manifest debe ser revisado por el operador antes de usarlo y debe contener sólo archivos propios o cuya lectura esté autorizada.

## Ejecución en Termux

```sh
pkg install python
python termux-server/server.py \
  --root ./received \
  --manifest ./manifest.json \
  --token 'cambia-este-token'
```

El transporte debe mantenerse en una red controlada. El servidor es receptor y no proporciona un explorador de archivos. No se deben incluir rutas de credenciales, bases de datos privadas, claves, memoria de procesos, dumps de kernel ni módulos protegidos.

## Estado de firmware

El manifiesto de ejemplo está etiquetado `13.52` porque el adaptador se diseñó para el proyecto de investigación, pero el protocolo es agnóstico al firmware. El repositorio no contiene una primitive WebKit operativa ni un lector nativo PS4; esas piezas deben permanecer fuera de este componente.

## Verificación

Las pruebas host-side deben usar archivos de fixtures creados por el operador, simular interrupciones y comprobar que un hash incorrecto o un ID no allowlisted sea rechazado. No se ejecutan ELF/BIN ni payloads.
