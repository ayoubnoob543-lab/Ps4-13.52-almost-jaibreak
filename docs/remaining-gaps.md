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
