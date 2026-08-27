# Estado consolidado seguro: PS4 13.02 y 13.52

## Alcance

Este documento consolida únicamente evidencia pública, artefactos locales y análisis estático. No ejecuta exploits, no produce cadenas ROP, no intenta escapes de sandbox y no convierte candidatos de bugs en una ruta de kernel R/W.

## Matriz comparativa

| Candidato o componente | 13.02 | 13.52 | Evidencia disponible | Bloqueo real |
|---|---|---|---|---|
| WebKit/JSC userland | Infraestructura histórica y referencias de userland; compatibilidad exacta no demostrada | Kit de análisis, `jordy_stage2.js`, firmas parciales y probe seguro; PSFree figura ausente | Código/documentación parcial | Falta módulo WebKit retail y primitive específica |
| CSSFontFace/UAF | Referencia histórica; la primitive antigua no se puede trasladar automáticamente | Alcance declarado por terceros, sin primitive publicada para 13.52 | Código y writeup de otras versiones | Falta layout y testcase de la revisión retail |
| Celsius/FFS | Candidato declarado hasta 13.04; 13.02 queda dentro del rango afirmado | No debe extrapolarse; no hay prueba de supervivencia | Fuentes secundarias y código FFS upstream | Falta PoC original, imagen UFS y primitive R/W |
| Netctrl/ucred | Candidato cercano a 13.00; 13.02 no está demostrado | No hay evidencia de compatibilidad | Código/documentación de versiones anteriores | Falta comparación de kernel y prueba específica |
| `patch_mount` | Offset publicado, función no identificada con bytes | No aplicable automáticamente | Tablas de offsets | Falta disassembly/XREF |
| PUP/PS4SYS 13.52 | No aplicable | Hay fragmentos y metadata de PS4SYS 13.52 | Bytes/manifest de PUP, sin descifrado | No contienen por sí solos una primitive WebKit |
| `libkernel_sys_13.52` | No aplicable | Hay blob y firmas parciales | Bytes/documentación de `libkernel_sys` | No es `libSceNKWebKit` ni prueba de userland |

## Estado de los candidatos

Los candidatos de bugs y los bytes presentes son útiles para clasificación y análisis estático, pero su existencia no demuestra una cadena funcional. Las referencias de `analysis/osint_universe/` contienen material histórico y posibles fuentes de userland, pero deben conservar su procedencia original y no mezclarse con los artefactos de PUP o con el `kpayload` posterior al kernel.

## Qué puede cerrarse sin hardware

Puede cerrarse documentalmente el inventario de ramas, hashes, manifests, formatos, dependencias, nombres de módulos, clasificación de candidatos y pruebas host-safe. También puede validarse la integridad de fragmentos PUP contra su manifest sin ejecutar ni descifrar su contenido.

## Qué no puede cerrarse sin un artefacto legítimo adicional

No puede confirmarse una primitive WebKit 13.52, un escape de sandbox, una equivalencia de offsets entre firmwares, la correspondencia de `patch_mount` con `ffs_mountfs`, Celsius en 13.02/13.52 ni kernel R/W. Para elevar esas afirmaciones hace falta un módulo WebKit retail o snapshot equivalente con procedencia, un testcase específico, una imagen UFS documentada o una prueba técnica autorizada.

## Conclusión

El repositorio contiene una base importante de análisis y varios candidatos, pero no una cadena operativa completa. La clasificación honesta es: **infraestructura y evidencia indirecta presentes; primitive de userland y transición a kernel no demostradas**.
