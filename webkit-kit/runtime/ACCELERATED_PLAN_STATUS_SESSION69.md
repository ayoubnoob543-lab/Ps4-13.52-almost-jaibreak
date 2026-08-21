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
