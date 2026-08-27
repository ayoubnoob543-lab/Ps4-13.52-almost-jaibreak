# Userland WebKit PS4 13.52 — baseline de trabajo

## Estado

Esta rama contiene una **base experimental de análisis y portabilidad**, no un exploit WebKit 13.52 funcional. La infraestructura reutilizable incluye `jordy_stage2.js`, herramientas de análisis de blobs, firmas parciales de `libkernel_sys_13.52`, documentación BD-J y stubs host-safe.

## Componentes reutilizables

| Componente | Estado | Uso permitido en esta base |
|---|---|---|
| Análisis de blobs y metadatos | `PORTABLE` | Inventariar formato, segmentos, hashes y candidatos de imports |
| Firmas parciales de `libkernel_sys_13.52` | `DIRECT_BYTES`/`STRUCTURAL` según entrada | Referencia documental; no sustituye WebKit retail |
| `jordy_stage2.js` | `SKELETON` | Revisar flujo y dependencias; no es una cadena ejecutable |
| `webkit_gadgets_1350.js` | `13.50_ONLY` | Referencia histórica; no transferir offsets a 13.52 |
| `orbis_webkit_stub.c` | `HOST_SAFE_STUB` | Pruebas locales de contrato y capacidades, sin módulos Sony |
| PSFree 13.52 | `ABSENT` | No se declara port hasta aportar fuente y validación |

## Bloqueos que no se deben ocultar

`analysis/psfree_porting.json` declara `status: ABSENT`. `tools/webkit_1352_migration.json` deja vacíos el artefacto WebKit, las bases de módulos, los patrones y los imports. `jordy_stage2.js` contiene marcadores `TODO` para la resolución de `dlsym` y del ancla de WebKit. El stub host-safe declara explícitamente que faltan módulos retail, ABI/sysroot, integración del proceso, política JIT/W^X y primitive de memoria.

Por ello, este documento no inventa direcciones ni convierte offsets de 13.50, 13.04 o 13.02 en offsets 13.52. El siguiente paso técnico legítimo es aportar un artefacto WebKit 13.52 con ruta, firmware, tamaño, hash y formato verificables; a partir de él se pueden ejecutar los escáneres estáticos existentes y rellenar únicamente los campos demostrados.

## Resultado

Se ha preparado la **base de userland 13.52**, entendida como organización, contratos, inventario y pipeline de análisis. Todavía no se ha producido un WebKit exploit, un escape de sandbox ni una cadena nativa reproducible para 13.52.

## Verificación local

Se comprobó la sintaxis del manifiesto JSON y el diff no presenta errores de whitespace. Las pruebas host-safe existentes no pudieron ejecutarse porque `pytest` no está instalado en el entorno actual; no se interpreta como fallo del código ni como validación de compatibilidad 13.52.

## Probe añadido

Se añadió `harness/userland_1352_capability_probe.js`. El probe sólo consulta capacidades estándar del runtime —BigInt, ArrayBuffer, WebAssembly, Promise, Proxy, Atomics, TextEncoder y URL— y emite un JSON con `safe_only: true`, `exploit_attempted: false` y `native_calls_attempted: false`. Se ejecutó correctamente con Node en el host. Este resultado valida el harness JavaScript, no el runtime retail de PS4 13.52.
