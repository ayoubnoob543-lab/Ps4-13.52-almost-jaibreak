# Matriz cruzada de evidencia PS4 13.52

Este documento consolida fuentes técnicas auditadas de forma estática. Los repositorios externos se leen como código y texto; no se importan, construyen ni ejecutan payloads, exploits o módulos recuperados.

## Estado de las fuentes

| Fuente | Commit auditado | Qué aporta | Clasificación | Qué no demuestra |
|---|---|---|---|---|
| `kmeps4/PSFree` | `368d82aa40d3017c220757ce315761adb5f06678` | `find_base`, resolución de imports RIP-relative, localización de `libkernel_web` mediante `rdlo` y escaneo de wrappers de syscall | `PORTABLE` | No aporta WebKit ni módulos 13.52; su configuración es histórica/default 9.00 |
| `ntfargo/CSSFontFace-Exploit` | `221baa6e7349b96a6fd299808a25a4178e47741c` | Layouts CSSFontFace históricos, campos `m_featureSettings`, vtables y arquitectura de UAF/ARW | `STRUCTURAL` / `PORTABLE` | No aporta layout 11.50+ o 13.52 ni una cadena runtime 13.52 |
| `Vuemony/vue-after-free` | `6e37d510c7383aac2378b7215aefd14c1defd8d1` | Separación explícita `userland.ts`/`kernel.ts`, descubrimiento de bases y manejo de `sysent[661]` | `PORTABLE` / `STRUCTURAL` | No es un dump de WebKit/kernel 13.52 y sus offsets no se transfieren |
| `ps4-linux/ps4-linux-loader` v25 | `9acef9fbf79097a2bb39d6c9c17228198bc445cc` | Bloque `PS4_13_52`, dispatch de firmware `1352`, campos como `pmap_protect`, `sysent`, `kernel_map` | `STRUCTURAL` | No contiene bytes de kernel retail 13.52; no convierte los offsets en `DIRECT_BYTES` |
| `libkernel_sys_13.52.bin` local | hash del manifest coincidente | Blob raw de 479232 bytes, chunks reconstruibles y wrappers directos/estructurales | `CONFIRMED_1352` para el artefacto; `DIRECT_BYTES` para stubs `0x215/0x216` | No valida WebKit, `libkernel_web`, kernel ni runtime |

## PSFree: piezas migrables

PSFree contiene tres técnicas transferibles como analizadores, no como valores:

1. `find_base()` avanza por páginas de 16 KiB hasta identificar límites de un segmento de módulo. Se conserva como mecanismo de descubrimiento, condicionado a que exista una primitive de lectura y un punto de referencia en la imagen objetivo.
2. `resolve_import()` reconoce el stub x86-64 `FF 25 disp32` y resuelve el puntero RIP-relative. Se conserva como parser estructural para GOT/PLT/imports.
3. El escaneo de `libkernel_web` busca la cadena `rdlo` y secuencias `mov rax, imm32; mov r10, rcx; syscall`. Se conserva como patrón candidato; necesita bytes de la misma build para ser útil en 13.52.

Los offsets de `module/offset.mjs` describen layouts JSC/WebCore históricos. Se clasifican como `REQUIRES_REANALYSIS` para 13.52.

## CSSFontFace: límite de la implementación pública

El README de CSSFontFace-Exploit afirma simultáneamente un alcance de vulnerabilidad PS4 6.00–13.52 y una implementación pública PS4 6.00–11.02. También declara que WebKit 11.5x–latest introdujo `m_propertiesOrCSSConnection` y que la primitive de lectura/escritura basada en `m_featureSettings` deja de ser utilizable sobre el rango soportado.

La tabla `constants.js` auditada contiene firmware keys sólo hasta 11.02. No existe un valor legítimo que pueda reutilizarse como 13.52. La migración implementada sólo extrae y clasifica campos; no inventa `sizeof`, vtable, offsets de miembros o gadgets para el nuevo WebKit.

## Vue-After-Free: separación de capas

`userland.ts` y `kernel.ts` muestran una separación útil:

```text
UAF / objetos JSC → leak y ARW userland → bases libc/libkernel
                                         → capa kernel separada
```

El hecho de que el código manipule `sysent[661]`, `JMP_RSI_GADGET` o estructuras kernel sólo demuestra que son parámetros dependientes de firmware. No existe una entrada pública suficiente para declarar Vue-After-Free compatible con 13.52 sin sus bytes y tablas de la misma build.

## Loader/Linux v25: valor de los offsets 13.52

El commit `9acef9f` añade un bloque claramente etiquetado `PS4_13_52` en `linux/magic.h` y una entrada normalizada `{ 1352, ... }` en `linux/fw_offsets.h`. El bloque enumera, entre otros:

```text
pmap_protect       0x58570
sysent             0x1102B70
kernel_map         0x22D1D50
kernel_pmap_store  0x1B2C3A0
pmap_extract       0x573D0
```

Estos valores quedan clasificados como `STRUCTURAL`: tienen contexto de firmware y uso en código, pero no hay bytes de kernel retail acompañantes dentro del repositorio. El candidato `0x110A760` y `pmap_protect=0x59DF0` no reciben soporte adicional de esta fuente.

## Ancla libkernel 13.52

El manifest local y sus validadores confirman:

```text
libkernel_sys_13.52.bin
size:   479232
sha256: ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c
```

Los chunks `lk_dump1.bin`, `lk_dump2.bin` y `lk_dump3.bin` coinciden por tamaño y SHA-256, y la reconstrucción coincide con el blob combinado. Los stubs de `jitshm_create`/`jitshm_alias` cargan `rax=0x215`/`0x216` y se mantienen como `DIRECT_BYTES`. Los demás wrappers permanecen `STRUCTURAL` según el manifest existente.

## Reglas de integración

No se integran offsets históricos directamente. La matriz de implementación sigue estas reglas:

| Tipo de dato | Tratamiento |
|---|---|
| Bytes del mismo artefacto 13.52 con hash coincidente | `CONFIRMED_1352` o `DIRECT_BYTES` |
| Patrón/estructura en código de una fuente con firmware explícito | `STRUCTURAL` |
| Algoritmo de búsqueda de módulo/import/GOT | `PORTABLE` |
| Tabla histórica sin bytes de la build objetivo | `REQUIRES_REANALYSIS` |
| Mención sin artefacto o sin segunda validación | `UNVERIFIED` |
| Módulo requerido que no está disponible | `ABSENT` |

## Bloqueos

Continúan ausentes `libSceNKWebKit.sprx` 13.52, `libkernel_web.sprx` 13.52, `libSceLibcInternal.sprx` 13.52, un kernel retail 13.52 y un SELF/eboot que permita correlacionar imports. Por ello permanecen pendientes la vtable CSSFontFace 13.52, `m_propertiesOrCSSConnection`, gadgets, GOT/PLT y la conexión binaria WebKit → libkernel.

No se ha demostrado jailbreak, ejecución de payload ni compatibilidad runtime en PS4 13.52.


## Búsqueda dirigida de artefactos WebKit 13.52

Se realizaron consultas exactas para `libSceNKWebKit.sprx`, `libkernel_web.sprx` y `libSceLibcInternal.sprx` junto con `13.52`. Las fuentes técnicas devueltas fueron las páginas de [Vulnerabilities](https://www.psdevwiki.com/ps4/Vulnerabilities) e [Internet Browser](https://www.psdevwiki.com/ps4/Internet_Browser) del PS4 Developer Wiki. Estas páginas documentan módulos, User-Agent y alcance histórico de vulnerabilidades, pero no contienen un archivo 13.52, hash, segmento `.text`, `PT_SCE_RELRO`, tabla de relocaciones o símbolos.

Clasificación: contexto de módulos y browser `DOCUMENTATION`; binarios WebKit 13.52 `ABSENT`; offsets y layout 13.52 `UNVERIFIED`.

## Cobertura ampliada del ancla libkernel

El manifest también registra `stat=0x15310`, `pwrite=0x15490`, `lseek=0x154f0`, `unlink=0x14930`, `socket=0x45f0` y `connect_alt=0xc970`. Todos proceden del mismo blob hashado y se mantienen `STRUCTURAL`; no son identificaciones runtime ni símbolos demostrados únicamente por el prólogo.
