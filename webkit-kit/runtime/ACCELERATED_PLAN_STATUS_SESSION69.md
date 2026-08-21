# Plan acelerado de WebKit/PS4 13.52 — sesión 69

## Objetivo

Dejar operativo el WebKit/JSC de laboratorio y preparado el análisis del WebKit retail, sin ejecutar exploits, payloads, binarios desconocidos ni interactuar con hardware.

## Estado verificable

| Línea | Estado | Bloqueo |
|---|---|---|
| Smoke ECMAScript seguro con Node | `PASS` | Es host-only y no demuestra WebKit PS4 |
| MiniBrowser WPE 2.52.6 | `BLOCKED` | El binario exige GLIBC 2.43/2.44 y bibliotecas WPE no disponibles en el prefix por defecto; con las bibliotecas del rootfs aparece incompatibilidad `__pointer_chk_guard/GLIBC_PRIVATE` |
| Fixtures DOM/CSS/JS | `PASS` en validación SHA-256 | La ejecución del MiniBrowser no llegó a procesarlas |
| WebKit-601-1300 | Fuente/referencia disponible | `JSCBRIDGE/Memory.h`, sysroot y port Orbis ausentes |
| Pipeline de análisis retail | Preparado | No hay `libSceNKWebKit.sprx`, `libkernel_web.sprx`, `libSceLibcInternal.sprx` ni `eboot.bin` en las raíces inspeccionadas |
| PUP 13.50/13.52 | Bytes preservados en rama privada | Metadata, tabla de segmentos y módulos internos siguen protegidos |

## Orden de trabajo

1. No tocar los PUP originales ni el rootfs WPE.
2. Mantener el smoke host como baseline reproducible.
3. Intentar reparar únicamente el entorno de laboratorio mediante dependencias públicas y aisladas; no copiar ni sustituir la libc del sistema.
4. Ejecutar el correlador sólo sobre fuentes locales y conservar `MATCH`, `PARTIAL MATCH` o `NO MATCH` junto con `UNVERIFIED` para 13.52.
5. Si aparece una muestra retail legítima, calcular primero hash, formato, arquitectura, Build ID y procedencia antes de leer funciones.
6. No intentar recuperar claves, descifrar fuera de un método autorizado ni inferir offsets desde la entropía.

## Criterio de parada de cada línea

La ruta de laboratorio se considera completada cuando el host smoke pasa o queda documentado con una causa reproducible. La ruta retail no se considera iniciada hasta que exista un artefacto de PS4 identificable; sin él, cualquier conclusión sobre una vulnerabilidad concreta permanece `UNVERIFIED`.

## Comprobación posterior

La búsqueda local no encontró un checkout materializado bajo `/home/ubuntu/ps4-lab-1352` ni directorios con nombre `WebKit-601-1300`; las referencias históricas permanecen en manifests, informes y objetos/corpus documentales ya inventariados. Por ello no se inicia una compilación histórica en esta iteración: primero habría que materializar legítimamente la fuente exacta y sus dependencias, sin confundirla con el runtime retail 13.52.

La inspección del directorio `webkit-kit/homebrew/wpe-source` encontró únicamente `wpebackend-fdo-1.16.1.tar.xz`; no hay allí un checkout fuente completo de WPE WebKit ni un árbol WebKit-601-1300 compilable. El siguiente trabajo de laboratorio debe centrarse en usar el WebKitGTK/JSC instalado o en materializar fuentes públicas verificables, no en tratar el tarball backend como si fuera el motor completo.

## Pasada pasiva sesión 70

El inventario actualizado de `/home/ubuntu/firmware-lab-runtime`, `/home/ubuntu/wpe-artifacts-2526` y `/home/ubuntu/Downloads` volvió a producir `found: []` y `No retail WebKit 13.52 module is present in scanned roots`. Los candidatos `libSceNKWebKit.sprx`, `libkernel_web.sprx`, `libSceLibcInternal.sprx` y `eboot.bin` permanecen `MISSING/UNVERIFIED`. Esta línea queda aparcada; no se repetirá hasta que aparezca un archivo nuevo en esas raíces.

## Política de aparcamiento

La línea de obtención de módulos retail y la línea de interpretación de los PUP quedan aparcadas. Sólo se reabrirán si aparece un artefacto nuevo con procedencia verificable, un hash/Build ID atribuible a PS4 13.52 o una salida autorizada de metadata/segmentos que no esté ya inventariada. No se repetirán las mismas URLs, repositorios, búsquedas de `libSceNKWebKit` ni escaneos locales sin cambios.

La línea activa queda limitada al mantenimiento reproducible del laboratorio: WebKitGTK host, smoke tests, hashes, tests estáticos y preparación del correlador. Ningún PASS de host se promocionará a evidencia retail.

## Estado de continuidad

La iteración 70 dejó el WebKitGTK host validado con un smoke de tres etapas y el pipeline estático en `9/9 PASS`. La búsqueda de artefactos retail no produjo módulos nuevos y queda aparcada con criterio de reapertura. La investigación no se considera finalizada: permanecerá abierta para incorporar únicamente evidencia nueva con procedencia verificable, sin repetir repositorios, URLs o escaneos sin cambios.
