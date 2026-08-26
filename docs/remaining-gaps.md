# BRECHAS RESTANTES — cierre offline total (2026-08-24)

Toda brecha restante converge en UN hito: **una sesión console-oracle en 13.52**
(kernel-exec + payload pup_decrypt adaptado). Tras ella, TODO lo demás se
resuelve OFFLINE desde Termux con herramientas ya creadas/documentadas:

1. .dec producido ⇒ tabla segmentos+metadata AES128 en claro (offset 0x20…)
2. Descifrado segmentos offline (AES128+IV de metadata + zlib) — implementable
   en Termux con cryptography/lzma (sin PS4)
3. system_fs_image.img extraído ⇒ montar FAT32/exFAT ⇒ kernel retail + módulos
   ⇒ offsets 13.52 verificables ⇒ cierra objetivos del lab
4. Con kernel retail: validar/refutar sysvsem(220/221/222), kqueue UAF window,
   semctl CVE-2026-58087 en binario real

Sin consola NO queda ninguna incógnita resoluble por vías públicas conocidas:
barridos GitHub/X/wiki/foros agotados (ver source-matrix y offline_scan.json).

Clasificación final de la cadena: ver docs/pup-crypto-chain-1352.md.

## NUEVA BRECHA TÉCNICA (kernel 11.02 real descargado y verificado)

Artefacto: `~/fl_verify/deep/kernel1102/11.02/kernel.bin` (44 MB,
sha256 `451f8735…` ✓, NO commiteado por regla no-blobs).
Tabla numerada extraída: `research/results/orbis1102_syscall_numbers_verified.txt`
(680 entradas, punteros→strings verificados).

| Incógnita nueva | Estado | Método propuesto |
|---|---|---|
| Localizar array `sysent[]` en binario stripado | DESCONOCIDO — layout Sony≠F9 stock (no hay runs {int,ptr} de 16B) | RE offline: probar layouts 24/32B, buscar por handlers conocidos (exit→sigthread), o anclar via llamadas desde sys_ioctl |
| Desensamblar handler __semctl (GETALL/SETALL) para verificar patrón CVE-2026-58087 EN BINARIO ORBIS | HIPÓTESIS→verificable offline una vez localizado sysent | capstone sobre sy_call del índice correspondiente |
| ¿Claves de cifrado PUP accesibles desde kernel x86? | HIPÓTESIS (SAMU probablemente las retiene) | strings/xrefs alrededor de sbl/pup_update.c module |

## AUDITORÍA/RONDA KERNEL 11.02 (2026-08-25)

Verificado por cross-check independiente:
- Los 4 sha16 de payloads ioctl capturados corresponden byte-exacto a slices del
  PUP fuente (HDR/SEG × UPDATE1/2), incluida la corrección de offset 1248≠1232.
- Parser selftest + AES128 selftest + validador 33/33 re-ejecutados desde
  entorno limpio: OK.
- exp01c_layout_verify existía SOLO local sin trackear (detectado; pendiente
  decidir si se commitea).

Nuevo artefacto analizado: **kernel Orbis 11.02 real** (44 MB,
`451f8735…`, NO commiteado):
| Hallazgo | Clase |
|---|---|
| `syscallnames[]` localizado (680+, file 0x1a5f450), entrada 0="syscall" | CONFIRMADO_OTRA_VERSION |
| Numeración resuelta con marcadores #N (delta −1): kqueue=362, kevent=363, __semctl=510, semget=221 | CONFIRMADO_OTRA_VERSION |
| SysV IPC completo compilado en kernel (__semctl/semget/semop/msg*/shm*) | CONFIRMADO_OTRA_VERSION |
| `pup_update0` driver = módulo SBL (`sys/internal/modules/sbl/pup_update/pup_update.c`) | CONFIRMADO_OTRA_VERSION |
| Interfaz kernel→SAMU por strings `gbase_{map,unmap,set_attr}_for_samu` + `gbase_vm_map_zone` | EVIDENCIA PARCIAL (sin RE de funciones) |
| Comparas SLB2 en código del kernel | EVIDENCIA PARCIAL |
| Localizar `sysent[]` en binario stripado | DESCONOCIDO — 2 falsos positivos descartados (freelist BSS @0x2296388; pool asserts @0x1b081a8; stride-24 @0xc0a010 descartado). Método siguiente: anclar por handler conocido vía xref al string "syscall" o RE del dispatcher |
| Verificar patrón CVE-2026-58087 en handler __semctl REAL | BLOQUEADO por sysent (anterior) |

## LOS 5 PENDIENTES MÁS IMPORTANTES (post-auditoría)
1. Cabecera interna descifrada 13.52 (4832 B) — abre tabla+claves AES128.
   REQUIRES console-oracle (una vez).
2. system_fs_image.img extraído → kernel retail 13.52 + módulos.
   REQUIRES ídem.
3. Ventana double-free observada en HW (persistencia stale-entry).
   REQUIRES consola (exp20/21 listos).
4. Info leak KASLR real — cero evidencia aún; candidatos offline agotados.
   REQUIRES_HARDWARE.
5. sysent[] en kernel dump 11.02 (offline factible pero costoso) → habilitaría
   verificación binaria de CVE-2026-58087 y del patrón knote/M_ZERO sobre
   binario Orbis REAL (11.02), reduciendo incógnitas transferibles a 13.52.

## RONDA RE KERNEL 11.02 — resultados finales (2026-08-25)

Análisis estático sobre `kernel.bin` real (44 MB verificado):
| Hallazgo | Clase |
|---|---|
| Zona UMA **"KNOTE" presente** (x2) — sustrato del UAF existe en binario Orbis | CONFIRMADO_OTRA_VERSION |
| SysV IPC completo (sem/msg/shm) compilado | CONFIRMADO_OTRA_VERSION |
| `pup_update0` = módulo SBL (`sbl/pup_update/pup_update.c`) | CONFIRMADO_OTRA_VERSION |
| Interfaz kernel→SAMU: familia `gbase_*_for_samu` (mapeo de memoria para el procesador seguro) | EVIDENCIA PARCIAL |
| Tabla `syscallnames[]` completa extraída y archivada | CONFIRMADO_OTRA_VERSION |
| Numeración exacta vs runtime | DESCONOCIDO (off-by-one sin resolver; marcadores #N sugieren −1) |
| `sysent[]` localización | DESCONOCIDO — densidad/strides fallaron; dump híbrido sin .data analizable completa |
| Verificación CVE-2026-58087 en handler __semctl REAL | BLOQUEADA por sysent |

Transferencia a 13.52: la existencia binaria de KNOTE/SysV/pup_update0 en 11.02
REFUERZA (no demuestra) que 13.52 los hereda — mismo árbol, sin anuncios de
remoción. Clasificación de cada uno para 13.52: HIPÓTESIS FUERTE.

## VERIFICACIÓN CRUZADA LIBKERNEL (2026-08-25)
- 387 stubs comunes a las 4 versiones (9.00–12.52); solo 678/679 eliminados en 11.02
- kqueue(362)/kevent(363): presentes en TODAS las versiones
- SysV IPC (221/222/510): AUSENTE en TODAS las variantes libkernel de juego
- Set de wrappers congelado desde 11.02: cero churn en tres versiones mayores

## 🆕 HALLAZGO MAYOR: Netctrl/Poopsploit — triple-free ucred hasta FW 13.00 (2026-08-25)

Fuente: repo `RiyonAbib07/ps-vue-jb-2.5` (creado 2026-03-11, TypeScript, 72KB)

### Arquitectura
| Componente | Vulnerabilidad | FW |
|---|---|---|
| WebKit userland | CVE-2017-7117 | 5.05–13.02 |
| Kernel: Lapse | PPPoE (TheFlow) | 1.01–12.02 |
| **Kernel: Netctrl** | **triple-free ucred vía netcontrol(99)** | **1.01–13.00** |

### Mecanismo verificado por análisis de código fuente
1. `socket(AF_UNIX)` + `netcontrol(NETEVENT_SET_QUEUE)` + `close()` → free ucred
2. `setuid(1)` → alloc nueva ucred (reclaim)
3. `close(dup(uaf_socket))` → double-free
4. Búsqueda de "twins" (sockets compartiendo ucred libre) → triple-free
5. Spray iov recvmsg para groom del heap
6. Spray rthdr IPv6 para localizar gemelos

### Clasificación
- Mecánica: CONFIRMADA por análisis de código fuente público (70KB TypeScript legible)
- Funcionamiento en HW 13.00: AUTHOR_REPORTED sin verificación independiente
- Relación CVE-2026-45251: usa el mismo patrón UaF-fd pero con trigger netcontrol específico PS4

### Implicancia para el lab
Si Netctrl funciona realmente en 13.52 (no solo 13.00), combinado con el userland
WebKit (CVE-2017-7117 que funciona hasta 13.02), existiría una cadena completa
userland→kernel R/W para 13.52. PERO esto requiere verificación en hardware.

## 🆕 ANÁLISIS DEL CÓDIGO FUENTE NETCTRL (2026-08-25, ronda final)

Fuente: `RiyonAbib07/ps-vue-jb-2.5/src/download0/kernel.ts`

### Qué contiene el código público

| Componente | 9.03–12.52 | 13.00 | **13.02** |
|---|---|---|---|
| Payload kernel completo (hex shellcode) | ✅ | ✅ | ❌ |
| Offsets mmap RWX | ✅ | ✅ [0x1fa77a] | ✅ [0x1fa78a] |
| Mapeo de versión a shellcode | ✅ | ✅ | ❌ |

### Implicación crítica
Alguien determinó los offsets de parche mmap para 13.02 específicamente,
lo que implica que tuvo acceso al binario del kernel 13.02 (o lo derivó
por diff con 13.00). Pero NO publicó el payload completo del exploit.

### La pieza exacta que falta para 13.02
El payload kernel completo para 13.02 = misma estructura que el payload de
13.00 pero con los offsets correctos del kernel 13.02. Los offsets necesarios:
- Direcciones base de las funciones a parchear (mmap RWX ya conocido)
- Direcciones de los syscalls a habilitar
- Dirección de las credenciales para setuid(0)

Estos offsets SOLO pueden determinarse teniendo acceso al binario kernel
13.02 (que está dentro del system_fs_image.img cifrado del PUP).

### Cadena 13.02: inventario de piezas

| Pieza | Estado | Fuente |
|---|---|---|
| WebKit userland (CVE-2017-7117) | ✅ funciona 5.05–13.02 | ps-vue-jb-2.5 README |
| Kernel exploit Lapse | ✅ hasta 12.02 | ídem |
| Kernel exploit Netctrl | ✅ hasta 13.00 / ❓ 13.02 | ídem |
| Offsets mmap RWX 13.02 | ✅ documentados | kernel.ts |
| Payload kernel completo 13.02 | ❌ NO EXISTE | — |
| Kernel retail 13.52 bytes | ❌ NO EXISTE | — |
| Confirmación HW 13.02 | ❌ nadie ha publicado | — |

## ANÁLISIS DEL SHELLCODE KERNEL 13.00 — qué parchea exactamente (2026-08-25)

Desensamblado del payload hex 13.00 (314 B): **12 parches al kernel**.
Todos escriben bytes en direcciones relativas a la base del kernel.

| # | Offset desde kernel base | Valor escrito | Función probable |
|---|---|---|---|
| 1 | `+0x00000ACD` | `0xEB` (JMP) | desactiva check |
| 2 | `+0x002BD42D` | `0xEB` | desactiva check |
| 3 | `+0x002BD471` | `0xEB` | desactiva check |
| 4 | `+0x002BD4ED` | `0xEB` | desactiva check |
| 5 | `+0x002BD531` | `0xEB` | desactiva check |
| 6 | `+0x002BD6DD` | `0xEB` | desactiva check |
| 7 | `+0x002BDB8D` | `0xEB` | desactiva check |
| 8 | `+0x002BDC5D` | `0xEB` | desactiva check |
| 9 | `+0x000004C2` | `0xEB` | desactiva check |
| 10 | `+0x00391546` | `0xEB` | sys_veri / verificación |
| 11 | `+0x001FA77A` | `0x37` | mmap RWX (byte 1) |
| 12 | `+0x001FA77D` | `0x37` | mmap RWX (byte 2) |

Para 13.02: SOLO se conocen los parches #11 y #12 (`[0x1fa78a, 0x1fa78d]`).
Los otros 10 offsets son DESCONOCIDOS sin el binario kernel 13.52/13.02.
Delta observado entre 13.00→13.02 en mmap: +0x10 bytes. NO extrapolable a
los demás sin el binario real.

Fuentes que confirman offsets mmap 13.02: Vuemony/vue-after-free,
RiyonAbib07/ps-vue-jb-2.5, rezaadi0105/vue-after-free — todos comparten
el mismo origen. Ninguno publica los otros 10 offsets.

## BÚSQUEDA EXHAUSTIVA DE LOS 10 OFFSETS FALTANTES PARA 13.02 (2026-08-25)

### Fuentes revisadas
- TODOS los forks de Vuemony/vue-after-free (15+, sin modificaciones relevantes)
- GitHub Code Search por cada offset individual (0x2bd42d, 0x2bd471, etc.)
- Búsqueda web en PSX-Place, PSXHAX, psdevwiki, Reddit
- Repos relacionados: SocraticBliss, zecoxao, fail0verflow/prosperous

### Resultado
Los 10 offsets faltantes **NO existen en ninguna fuente pública**:
| Offset (13.00) | Buscado | Encontrado |
|---|---|---|
| +0x00000ACD | ✓ GitHub code search | Nada |
| +0x002BD42D | ✓ GitHub code search → solo kexploit.js 9.00 (FW distinto) | N/A para 13.02 |
| +0x002BD471 | ✓ ídem | N/A |
| +0x002BD4ED | ✓ ídem | N/A |
| +0x002BD531 | ✓ ídem | N/A |
| +0x002BD6DD | ✓ ídem | N/A |
| +0x002BDB8D | ✓ ídem | N/A |
| +0x002BDC5D | ✓ ídem | N/A |
| +0x000004C2 | ✓ GitHub code search | Nada |
| +0x00391546 | ✓ GitHub code search | Nada |

### Verificación de procedencia de los offsets mmap 13.02
Commit `50cd384f` (Vuemony, 2026-02-08): añadió [0x1fa78a, 0x1fa78d]
junto con 12.50 y 13.00 en un solo commit. Sin evidencia independiente
de análisis del binario kernel 13.02. Clasificación elevada a UNVERIFIED
(antes: VERIFIED_METADATA — corrección necesaria).

### Conclusión definitiva
La cadena 13.02 NO puede reconstruirse con material público porque
faltan 10 offsets que solo existen dentro del kernel retail cifrado.
El único camino es: consola-oracle → .dec → extraer kernel binario →
calcular offsets → publicar. Un solo acceso resuelve el problema permanentemente.

## BARRIDO FINAL DE ARTEFACTOS PÚBLICOS 13.02 (2026-08-25)

Búsqueda exhaustiva en GitHub Code Search + repos + web: **NINGÚN artefacto
público nuevo encontrado** para kernel retail 13.52, system_fs_image.img,
libkernel_sys/libkernel_web 13.52, o WebKit 13.52.

Fuentes revisadas sin resultados nuevos:
- GitHub Code Search (system_fs_image, libkernel_sys 13.52, SYSENT 1352)
- Todos los repos de ps4boot (releases v54/v19 solo contienen loaders Linux)
- RPCSX/orbis-kernel (RE de FreeBSD port, no dump real)
- jevinskie/ps4-kern-dump (herramienta, no dump)
- JRRN/Pupx (parser Python de PUP, no descifrador)
- ntfargo/CSSFontFace-Exploit (ya auditado previamente)

Conclusión: los artefactos que faltan SOLO pueden obtenerse ejecutando código
en una consola 13.52 con kernel-exec activo. Ninguna fuente pública alternativa
existe a fecha de hoy.
