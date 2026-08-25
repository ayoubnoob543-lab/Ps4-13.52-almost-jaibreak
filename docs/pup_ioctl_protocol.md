# Protocolo ioctl de /dev/pup_update0 — capturado con mock (PS4 13.52)

Fecha: 2026-08-24 · Método: `ps4-pup_decrypt` (idc) portado a host Termux con
shim de interceptación `open/ioctl` → servidor mock AF_UNIX
(`research/experiments/exp30_ioctl_mock/`).

## Secuencia observada sobre PS4UPDATE.PUP 13.52 real

Por cada PUP interno (UPDATE1 326 MB, UPDATE2 177 MB):

| # | ioctl | Opcode | args_len | payload | Contenido del payload |
|---|---|---|---|---|---|
| 1 | DECRYPT_HDR | `0xC0184401` | 24 B | 4832 B / 1248 B | cabecera interna CIFRADA completa (16 B claros: magic `4F153D1D` + versión/flags; resto ciphertext) |
| 2 | VERIFY_SEG_ADD | `0xC0184402` | 24 B | 64 B | segmento firma adicional (idx=2 según tabla MOCK) |
| 3 | VERIFY_SEG | `0xC0184403` | 24 B | 64 B | segmento watermark (idx=1) |
| 4 | DECRYPT_SEG | `0xC0184404` | 24 B | 65536 B | datos cifrados REALES leídos del fichero (sha16 `ce92a785…` UPD1, `77ba7473…` UPD2) |

Después: saltos de watermark/firma y paso al siguiente PUP. Sin bloques
(0xC0284405) en esta captura porque la tabla MOCK no marcaba flag 0x800;
la estructura del bloque está documentada por código en §estructuras.

## Estructuras (verificadas por código + captura)

```c
// args comunes 24 B (ioctls 01–04):
struct { void *buffer; size_t length; uint16_t index; /*pad*/ int type_ó_; }
// variante verify: { u16 index; pad; void *buffer; size_t length; }
// bloques 40 B (0xC0284405):
struct { u16 entry_index; u16 block_index; void *block_buf;
         size_t block_len; void *table_buf; size_t table_len; }
```

Respuesta del kernel: el buffer se modifica IN-PLACE (descifrado) y el valor de
retorno es 0/-errno. En la captura MOCK las respuestas están marcadas:
cabecera sintética con tag `MOCKHDR`, segmentos devueltos sin descifrar
(passthrough del propio ciphertext enviado).

## Hallazgos clave

1. **El tool no contiene criptografía**: toda la operación es delegar buffers al
   kernel vía estos 5 ioctls. Las claves y el AES viven en el SBL/kernel.
2. **La cabecera interna viaja cifrada COMPLETA** (4832 B): la tabla de segmentos
   solo existe tras el descifrado en-kernel ⇒ imposible enumerar segmentos
   reales offline.
3. **Los payloads que circulan son bytes reales del firmware 13.52**: los sha256
   capturados (ver results/) son material de verificación para cualquier
   implementación futura.
4. ABI: los opcodes viajan como `int` con signo (sign-extension a 64 bits en el
   syscall); el kernel usa los 32 bits bajos.

## Reparto Termux vs PS4

| Componente | Termux |
|---|---|
| Orquestación BLS→PUP→segmentos (pup_orchestrator.py) | ✅ |
| Emisión/captura de ioctls contra mock (shim + pup_decrypt_mock) | ✅ |
| Descifrado real (header/segment/bloque) | ❌ REQUIRES_PS4_KERNEL (`/dev/pup_update0`) |

## Reproducción

```bash
cd research/experiments/exp30_ioctl_mock
python3 run_experiment.py        # lanza mock+hilo, payload, y guarda resultados
# logs: ioctl_log.jsonl · payload_stderr.log · result_summary.json
```

---

## PROFUNDIZACIÓN: reconstrucción byte-exacta de los args de 24 B (2026-08-24, ronda 2)

Captura con `args_hex` completo (`srv.log` → 8 frames). Validación contra las
structs del código fuente: **coincidencia total, sin campos inventados**.

### DECRYPT_HDR (0xC0184401) — captura UPDATE1 (#1) y UPDATE2 (#5)

```text
args[24]: 00 c0 61 3c 6f 00 00 b4 | e0 12 00 00 00 00 00 00 | 00 00 00 00 00 00 00 00
          └── buf_ptr (8B) ──────┘ └── length (8B)=4832 ──┘ └─ type(4B)=0 ─┘─pad(4B)─┘
UPDATE2:  00 00 62 bc …        | e0 04 00 00 … = 1248    |
```

| Off | Tamaño | Campo | Significado | Captura #1 |
|---|---|---|---|---|
| 0x00 | 8 | buffer | puntero user al header cifrado (in-place) | 0xb400006f3c61c000 |
| 0x08 | 8 | length | tamaño cabecera = unk_0C+unk_0E | 4832 ✓ (=0x12E0) |
| 0x10 | 4 | type | translate_type(pup_type); decrypt.c pasa literal 0 | 0 ✓ |
| 0x14 | 4 | padding | alineación struct a 8 | 00000000 ✓ |

### VERIFY_SEG_ADD/VERIFY_SEG (02/03) — capturas #2/#3/#6/#7

```text
args[24]: 02 00 00 00 00 00 00 00 | 00 00 62 bc 6f 00 00 b4 | 40 00 00 00 00 00 00 00
          └ idx(u16)+pad[6] ─────┘ └── buffer (8B) ─────────┘ └── length=64 ────────┘
```

| Off | Tamaño | Campo | Captura |
|---|---|---|---|
| 0x00 | 2 | index (índice de segmento en tabla) | 2 / 1 ✓ |
| 0x02 | 6 | padding | 000000000000 ✓ |
| 0x08 | 8 | buffer (64 B del segmento firma/watermark) | 0xb400006fbc620000 |
| 0x10 | 8 | length | 64 ✓ |

### DECRYPT_SEG (04) — capturas #4/#8

```text
args[24]: 00 00 00 00 00 00 00 00 | 00 40 10 6d 70 00 00 b4 | 00 00 01 00 00 00 00 00
          └ idx=0 + pad ─────────┘ └── buffer ───────────────┘ └── len=0x10000 ──────┘
```
idx=0 (primer segmento real), buffer apunta a 64 KB de CIFRADO REAL leído del
PUP (sha16 `ce92a785…` UPD1 / `77ba7473…` UPD2 — material verificado para
cualquier implementación futura).

## Rastreo público de opcodes (GitHub Code Search, 2026-08-24)

Todas las referencias a 0xC0184401–05 provienen de UNA misma familia:
`idc/ps4-pup_decrypt` (origen) · PSTools/ps4_unjail (`encryptsrv.c`, revela el
nombre del subsistema: *encryption service*) · andy-man · Scene-Collective ·
vvsx87/PPPwn · Creeeeger/PS4-dec · zecoxao/ps5-pup-decrypt(-elf) (PS5).
Ninguna implementación del BACKEND (lado kernel) está publicada.

## PS4 vs PS5 (prosperous/zecoxao)

| Operación | PS4 opcode | PS5 opcode |
|---|---|---|
| Verify BLS header | (integrado en flujo BLS externo) | `0xC0104401` (args 16 B, op dedicado) |
| Decrypt header | `0xC0184401` | `0xC0184402` |
| Verify watermark/additional | `0xC0184402` / `0xC0184403` | `0xC0184404` |
| Decrypt segment | `0xC0184404` | `0xC0184405` |
| Decrypt segment block | `0xC0284405` | `0xC0284406` |

Diferencias: PS5 añade verify-dedicado de cabecera BLS y desplaza +1..+2 los
demás; mismo tipo 'D' (0x44), mismos tamaños de args (24/40). Mismo dispositivo
`/dev/pup_update0` en ambas.

## Backend: qué depende exclusivamente del kernel/SBL

Modelo de referencia ([RuxaXa/ps4-research `pup-update0-samu-model.md`](https://github.com/RuxaXa/ps4-research)):
`ioctl → kernel PUP manager → mailbox seguro → SAMU (procesador de seguridad
AMD) con key-slots → retorno in-place`.

- Las claves residen en **key-slots de SAMU**: nunca visibles para el código
  x86 ni siquiera en modo kernel (pregunta abierta #8 del modelo: raw /
  derivada / slot-referenced / never-x86-visible).
- El AES y la verificación se ejecutan en el procesador seguro, no en el x86.
- Consecuencia: **un dump del kernel x86 13.52 NO bastaría** para construir un
  decryptor offline; haría falta replicar el diálogo con SAMU (mailbox) o
  ejecutar en consola.
- Estado del backend: sin implementación pública; solo este modelo testable.

## Validación contra bytes capturados

- 8/8 frames: args_hex coincide con las structs del código fuente campo a
  campo (incluidos paddings en cero).
- `length` de HDR == 4832/1248 == unk_0C+unk_0E reales del PUP ✓.
- `type=0` consistente con `decrypt_pup_data()` que pasa literal 0
  (el `state.pup_type` está comentado en la llamada original).
- `index` refleja la tabla MOCK sintética (0/1/2): valida estructura, no la
  tabla real de Sony (que solo existe tras descifrar cabecera).

## REQUIRES_HARDWARE / KERNEL
- Respuestas reales del backend SAMU (hoy: MOCK marcado).
- Tabla de segmentos verdadera del 13.52.
- Cualquier afirmación sobre claves: prohibido especular; modelo dice
  "never x86-visible" como hipótesis principal.

---

## RESPUESTAS DE CADA IOCTL Y PAPEL DE SAMU (investigación pública, 2026-08-24)

### Qué responde cada ioctl (deducido de código + comportamiento documentado)

No existe estructura de respuesta independiente: **la "respuesta" ES el buffer
de entrada modificado in-place** (descifrado/verificado) + valor de retorno
entero. Evidencia: `decrypt.c` escribe `buffer` al fichero de salida DESPUÉS del
ioctl sin transformar nada más (`fwrite(buffer, unencrypted_size, …)`).

| ioctl | Éxito | Modificación del buffer | Fallo |
|---|---|---|---|
| DECRYPT_HDR 0xC0184401 | 0 | cabecera interna descifrada in-place (tabla de segmentos pasa a claro) | −errno (p.ej. versión < instalada, product-code distinto — README idc) |
| VERIFY_SEG_ADD 02 | 0 | sin cambios (verificación) | −errno |
| VERIFY_SEG 03 | 0 | sin cambios | −errno |
| DECRYPT_SEG 04 | 0 | segmento descifrado (y descomprimido si flag 0x8) in-place | −errno |
| DECRYPT_SEG_BLK 05 | 0 | bloque descifrado usando tabla ya en clara | −errno |

Errores documentados por idc: el kernel rechaza updates más antiguos que el FW
instalado y de product-codes distintos (retail no descifra test/debug).

### Qué hace exactamente SAMU

Fuentes: psdevwiki («AMD SAMU — Secure Asset/Access Management Unit,
procesador separado que gestiona las tareas de cifrado/descifrado del PS4»),
CTurt («podemos interactuar para descifrar casi todo, pero es imposible extraer
claves para descifrar externamente»), marcan 2013, modelo RuxaXa.

```text
ioctl userland → driver pup_update0 (x86 kernel)
   → SceSblUpdateMgr / capa SBL
      → mailbox seguro hacia SAMU (ARM TrustZone-ish, HSM físico)
         · recupera key-slot apropiado (nunca expuesto)
         · ejecuta AES dentro del procesador seguro
         · devuelve plaintext al buffer x86
```

- Las claves viven en key-slots de SAMU: **never x86-visible** (hipótesis
  principal de la escena desde marcan 2013; nunca refutada).
- Consecuencia arquitectónica: ni un dump completo del kernel x86 13.52 permite
  construir un decryptor offline; el descifrado SIEMPRE requiere la consola
  (o replicar el protocolo de mailbox del SAMU, desconocido públicamente).

### ¿Backend/emulador público adaptable?

Barrido exhaustivo (GitHub/X/wiki/foros): **NO EXISTE**. Lo más cercano:
- payload idc + forks (consola obligatoria);
- prosperous PS5 (mismo diseño, otra plataforma);
- modelos de investigación (RuxaXa) que describen la interfaz pero sin backend.
Cualquier herramienta que anuncie "descifrar PUP PS4 en PC" sin consola carece
de base pública conocida y debería tratarse como sospechosa.

## Estado final de la investigación de protocolo
- Formato de peticiones: COMPLETO (capturado byte-exacto, validado contra código).
- Formato de respuestas: definido operativamente (in-place + retval); contenido
  real SOLO obtenible en consola con kernel exploit activo.
- Backend: SAMU/HSM — fuera de alcance por diseño de Sony; documentado como
  REQUIRES_PS4_KERNEL permanentemente.


## ACTUALIZACIÓN CRÍTICA (ronda final offline): formato interno documentado públicamente

psdevwiki/PUP (ed. 2026-06-28) documenta el formato que estábamos reconstruyendo
a ciegas: **ScePupMetadataEntry (0x50 B) contiene AES128 key+IV+HMAC digest+key
POR SEGMENTO**, dentro de la región cifrada de la cabecera. La cabecera se cifra
bajo clave **estática por firmware** ⇒ la brecha de descifrado es UNA sola clave,
no el SAMU por operación. Transcripción completa y tabla de índices ID→componente:
`analysis/sources/psdevwiki/PUP_format_snapshot.md` · hallazgos en
`research/results/offline_scan.json`.

---

## ✅ VALIDACIÓN END-TO-END OFFLINE DEL PIPELINE (2026-08-24, ronda final)

**Herramienta nueva**: `tools/pupdec_unpack.py` (desempaquetador .dec offline)
+ `tools/pupdec_validate_log.py` (validador contra log real de consola).

**Validación maestra**: reconstrucción sintética del contenedor a partir del log
REAL de consola (`analysis/sources/unpup4.log1`, masterzorag — FW antiguo,
UPDATE1 de 206 MB, 32 entradas) ⇒ el parser regeneró **33/33 comandos dd
idénticos** (skip/count exactos), incluida la tabla hash.bin separada
(headerSize=1632, hashSize=2816, entryCount=32).

**Reglas empíricamente confirmadas por el log**:
- Entradas de 32 B: `{u32 flags; u32 pad; u64 offset_abs; u64 csize; u64 usize}`
- Compresión zlib cuando `flags&8` (coincide 100% con los `openssl zlib -d` del
  log); csize<usize ⇒ inflate.
- Tabla hash independiente tras headerSize.

**Capa AES128 implementada y probada**: roundtrip CBC 9728 B OK (clave
sintética marcada como PRUEBA — no es material Sony). Lista para consumir las
keys/IVs de una metadata real cuando exista el primer .dec de 13.52.

## Conclusión operativa final
Todo lo posterior al primer plaintext (.dec) está implementado y validado
offline. La única pieza que exige consola sigue siendo producir ese .dec una
vez (kernel-exec → payload ioctl). Tras ello, Termux extrae kernel retail,
secure_modules y system_fs completo sin depender de la PS4.

---

## KERNEL ORBIS 11.02 REAL — análisis binario (2026-08-25)

Fuente: adjunto público `11.02.zip` (issue ps4-linux-payloads-archive#5),
`kernel.bin` 44.040.192 B, ELF x86-64, sha256 `451f8735…` ✓ verificado.
Archivo local: ~/fl_verify/deep/kernel1102/11.02/kernel.bin (NO commiteado, regla no-blobs).

### Hallazgos binarios [CONFIRMADO_OTRA_VERSION]
1. **Tabla de nombres de syscalls visible en claro** (585 entradas extraídas,
   `research/results/orbis1102_syscall_names.txt`): exit/fork/read… hasta +
   585. Incluye compat (freebsd4/7), observaciones obs_* (Sony) y reservados "#N".
2. **SysV IPC COMPLETO compilado en kernel**: __semctl (dos entradas: compat+
   nativa), semget, semop, msgget/msgsnd/msgrcv/msgctl, shmat/shmctl/shmdt/shmget.
   ⇒ CVE-2026-58087 (semctl TOCTOU) aplica a un kernel Orbis REAL (11.02);
   extrapolación a 13.52 = HIPÓTESIS fuerte (mismo árbol).
3. **pup_update0 driver PRESENTE**, con ruta de build embebida:
   `W:\Build\J02660907\sys\internal\modules\sbl\pup_update\pup_update.c`
   ⇒ pertenece al módulo SBL (`sbl_driver.sbl_service.sbl_chunk.sbl_sm_service`).
4. **Interfaz kernel↔SAMU identificada por strings**: familia
   `gbase_map_for_samu / gbase_unmap_for_samu / gbase_set_attr_for_samu /
   gbase_vtophys / gbase_vm0_vtophys` + zona `gbase_vm_map_zone`
   ⇒ el x86 SOLO prepara mapeos de memoria para el procesador seguro.
5. Comparas SLB2 en código (validación de contenedor en kernel) ✓.

### Discrepancia de numeración [DESCONOCIDO]
Secuencia de nombres sugiere kqueue≈311/kevent≈312, pero el runtime PS4 usa
362/363 (Luac0re+investigador). Causas posibles: entradas multi-nombre,
huecos "#N" mal contados, o tabla sysent≠tabla de nombres. RESOLVER con RE
del binario (localizar sysent array) — pendiente offline factible.

### Implicancia para 13.52
- sysvsem presente en 11.02 ⇒ HIPÓTESIS reforzada (no confirmada) para 13.52.
- pup_update0 presente ⇒ el device existe; acceso sigue REQUIRES_KERNEL_EXEC.
- Numeración divergente ⇒ NO usar números F9-stock ni asumir los del runtime
  sin verificar contra sysent real.

## RESOLUCIÓN FINAL DE NUMERACIÓN (kernel 11.02 real)

Array `syscallnames[]` localizado en file `0x1a5f450` (680+ punteros), comenzando
con `"syscall"` (=número 0, la instrucción syscall envuelta) seguido de
exit=1, fork=2, read=3… ⇒ **numeración 0-based confirmada doblemente**
(marcadores #N con delta constante −1 + secuencia completa).

| Syscall | Nº Orbis 11.02 |
|---|---|
| kqueue | **362** ✓ (coincide con runtime/investigador) |
| kevent | **363** ✓ |
| __semctl | **510** ✓ (coincide con SYS___semctl userland F9.1) |
| semget | 221 · semop | 222 |

**SysV IPC COMPLETO presente en kernel Orbis 11.02** [CONFIRMADO_OTRA_VERSION]:
__semctl(510), semget(221), semop(222), msgget(202?), shm*(205-232)…
⇒ CVE-2026-58087 aplicable al árbol Orbis [CONFIRMADO_OTRA_VERSION];
extrapolación a 13.52 = HIPÓTESIS fuerte (mismo árbol, sin parche anunciado).

**Pendiente**: localizar `sysent[]` (array de handlers) — dos candidatos
descartados (freelist BSS y pool de panics); método siguiente: anclar por
handler conocido vía xrefs al string "syscall"/patrones de dispatch.
