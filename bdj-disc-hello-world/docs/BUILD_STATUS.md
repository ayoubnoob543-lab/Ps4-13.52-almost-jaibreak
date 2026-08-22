# Build status

## Confirmado

El proyecto contiene un Xlet benigno `bdj.HelloWorldXlet` que implementa el ciclo de vida `initXlet`, `startXlet`, `pauseXlet` y `destroyXlet`. La lógica sólo crea una escena AWT/BD-J y pinta texto. No contiene referencias a carga dinámica, procesos, red, reflexión, `Unsafe`, filesystem privilegiado, código nativo ni payloads.

La validación estática propia genera `docs/validation.json` y ha confirmado que el árbol mínimo existe, que no aparecen referencias prohibidas y que no se ha probado hardware.

## Bloqueo actual

No se ha generado una ISO porque el repositorio no contiene una definición de plataforma/stubs BD-J verificable en `lib/bdj.jar`, `lib/classes.zip` ni `platform/bdj.jar`. Tampoco contiene todavía las herramientas externas de authoring necesarias para producir de forma reproducible BDJO/BDMV.

No se debe crear un `bdj.jar` ficticio ni marcar la ISO como generada. La siguiente dependencia legítima es un SDK/stub BD-J público y compatible, seguido de un empaquetado BDMV/BDJO reproducible.

## Estado

- `iso_generated`: `false`
- `hardware_tested`: `false`
- `mode`: `static-only`
- Compatibilidad con PS4 13.52: `UNVERIFIED`
- Native usermode o jailbreak: fuera de alcance
