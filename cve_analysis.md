# CVE Analysis for PS4 Kernel (Orbis OS / FreeBSD 9)

## kqueue/knote UAF en 13.52 — CONFIRMADO EN HARDWARE (autor-reportado) 🔥

- **Type:** CWE-416 Use-After-Free en subsistema BSD kqueue/knote
- **Trigger:** `kqueue` + `pipe()` + attach `EVFILT_READ` + `close(fd)`: `knlist_remove()`
  libera el knote mientras `kqueue_scan()` puede conservar referencia
- **Reclaim:** sprays de 50/100/200 knotes `EVFILT_USER` reocupan el slot de 0x80 B con
  ejecución estable del escenario (sin spray: kernel crash)
- **Leak hunt:** ~760 KB examinados vía kern.*, kinfo_proc, /dev/gc, /dev/random,
  eventos y scans libkernel ⇒ **0 punteros de kernel** (kinfo_proc devuelve direcciones
  sanitizadas)
- **Bloqueadas por sandbox UID=1:** fcntl, dup2, sendmsg, bind, thr_self, closefrom,
  BPF, IPv6 socket
- **Crashes adicionales observados:** `fstat`, `kldstat`, `kern.49` → aislar como bugs
  candidatos independientes o sondas de corrupción residual
- **Numeración PS4:** `EVFILT_USER=-7`, `EVFILT_FS=-8` difiere de stock FreeBSD →
  personalización Sony; diff pendiente contra bytes retail
- **Estado:** `CONFIRMED_CRASH_REPRODUCIBLE_AUTHOR_REPORTED`; faltan info leak y control
  fiable de `kn_fop@0x68`. Detalle completo:
  `analysis/kqueue_uaf_1352_observations_v2_2026-08-24.json`


## CVE-2026-58087 — semctl(2) GETALL/SETALL TOCTOU 🔥🔥 MÁXIMO CANDIDATO 13.52

- **Type:** TOCTOU race → heap OOB read/write kernel → posible elevación de privilegios
- **Component:** `sys/kern/sysv_sem.c` — comandos GETALL/SETALL de semctl(2)
- **Descubrimiento:** Maik Muench (Secfault Security), reportado a FreeBSD 2026-07-29;
  advisory [FreeBSD-SA-26:54.sysvsem](https://www.freebsd.org/security/advisories/FreeBSD-SA-26:54.sysvsem.asc)
- **Bug:** se registra el número de semáforos del set, se suelta el lock, se aloca un
  buffer con ese tamaño y se re-adquiere el lock. La validación usa el número de
  secuencia del set, que **envuelve tras 0x8000 ciclos de crear/destruir**. Un proceso
  atacante recreando sets a alta velocidad en el mismo índice hace pasar un set con
  otro número de semáforos ⇒ el `copyin/copyout` posterior lee/escribe fuera del buffer.
- **Impacto declarado:** *"An unprivileged local user can trigger out-of-bounds reads
  and writes on kernel heap memory, potentially leading to privilege escalation."*
- **Aplicabilidad PS4 13.52:**
  - psdevwiki (página Bugs, sección "Kernel → Untested"): **Patched: NO as of PS4 13.52
    and PS5 13.60. PS4 and PS5 may be affected.**
  - El bug es lógico y antiguo: presente en la base FreeBSD heredada por Orbis.
  - El fix upstream sustituye KASSERTs por runtime checks — los asserts no existen en
    kernels release como el de Sony, lo que hace plausible que el patrón vulnerable
    esté intacto.
  - Requiere invocar semctl(2) desde userland nativo: alcanzable vía entry points
    userland 13.52 (ver `docs/mast1c0re-artifacts.md`).
- **Estado real:** **UNTESTED_ON_CONSOLE / NO_PUBLIC_EXPLOIT_PS4**. Nadie ha publicado
  implementación ni confirmación en hardware. Es el primer bug kernel post-13.50 sin
  parche declarado — prioridad máxima de análisis para este lab.
- **Verificación estática contra FreeBSD 9.1 (2026-08-24)**: el patrón vulnerable existe
  VERBATIM en `sys/kern/sysv_sem.c` (~L737–767, fuentes archivadas en
  `analysis/sources/freebsd-9.1/`, SHA-256 en `SHA256SUMS`):
  ```c
  count = semakptr->u.sem_nsems;      /* snapshot */
  mtx_unlock(sema_mtxp);              /* suelta lock */
  array = malloc(sizeof(*array)*count, M_TEMP, M_WAITOK);
  mtx_lock(sema_mtxp);
  semvalid(...)                       /* chequeo seq — envuelve a 0x8000 */
  KASSERT(count == ...sem_nsems, ("nsems changed"));  /* ¡no-op en release! */
  for (i = 0; i < semakptr->u.sem_nsems; i++)   /* usa count NUEVO → OOB WRITE */
          array[i] = u.sem_base[i].semval;
  copyout(array, arg->array, count * sizeof(*array)); /* count VIEJO */
  ```
  El comentario original del código ADMITE el wrap de 0x8000 y confía en el KASSERT,
  que está compilado fuera en kernels release como Orbis. Dos direcciones de primitiva:
  - **OOB write con contenido controlado**: si el set de reemplazo tiene MÁS semáforos,
    se escriben `(nuevo-viejo)*2` bytes fuera del buffer con `semval` u16 pre-configurables
    por SETVAL (0..32767) sobre el set propio.
  - **Disclosure residual**: si el set nuevo es MÁS PEQUEÑO, el `copyout` con el count
    viejo devuelve bytes residuales del heap M_TEMP no sobrescritos ⇒ candidato a leak.
- **Candidatos de reclaim descartados/refinados**:
  - `msgsnd`: DESCARTADO como reclaim directo — F9 usa pool fijo prealocado (`msgpool`,
    sysv_msg.c L206) y headers de freelist estática, sin mallocs por mensaje.
  - `knote_zone`: los knotes viven en UMA zone dedicada (`kern_event.c` L183), NO en el
    malloc genérico ⇒ el array del semctl (M_TEMP) y los knotes son heaps separados; la
    combinación UAF+semctl exige puentes indirectos (grooming de vecinos en M_TEMP para
    el overflow, disclosure para KASLR).
- **Gate crítico pendiente de test**: `prison_allow(td->td_ucred, PR_ALLOW_SYSVIPC)`
  (L593) — si el sandbox UID=1 corre sin ese permiso, semctl/semop devuelven ENOSYS
  antes de tocar nada. Experimento #0: sondear disponibilidad de semsys bajo sandbox.
- **Clasificación:** `STRUCTURAL_HIGH_PRIORITY` (bug upstream confirmado + estado
  no-parcheado declarado por wiki; verificación en consola pendiente de terceros).

## Otros bugs "untested" relevantes de psdevwiki/Bugs (2026-08)

| Bug | CVE | Estado 13.52 |
|---|---|---|
| UaF en IPV6_MSFILTER socket option | CVE-2026-49412 | Maybe patched since 13.52 |
| UaF via file descriptor syscalls | CVE-2026-45251 | No as of 13.50; "maybe not affected" |
| Stack overflow via setcred(2) | CVE-2026-45250 | No as of 13.02; "maybe not affected" |
| WebKit JSCell::toX (type confusion) | sin CVE público | Funciona 6.00–11.02; OOM 11.50–13.50; "Maybe fully on 13.52" — sin prueba en consola |

## exFAThax v2 — UVFAT_readupcasetable Roundup Overflow ❌ PATCHED EN 13.52 (reportado)

- **Type:** Integer overflow → kernel heap corruption (DoS confirmado)
- **Component:** `UVFAT_readupcasetable` / `UVFAT_copyupcasetable` (driver exFAT del kernel)
- **Bug:** `table_len = (data_len - 1) + blsize` con chequeo con signo `if (-blsize < data_len)`:
  un `data_len` negativo grande hace que el roundup produzca un `table_len` menor que
  `blsize`, que se pasa a `sceFatfsCreateHeapVl()`; el buffer pequeño se desborda al
  rellenarlo vía `UVFAT_ReadDevice()`.
- **Descubrimiento:** ASaudidos (reportado a Sony 2026-05-08); PoC de kernel panic por
  CelesteBlue (2026-06-25). Documentado en psdevwiki como "FW <= 13.50 - exFAT driver
  integer overflow leading to DOS (exFAThax v2)".
- **Rango afectado:** 9.03–13.50 (v1, CVE-2022-3349 de TheFloW, era ≤9.00).
- **Mecánica exacta con los valores canónicos (`blsize=0x200`, `data_len=-1`):**
  ```text
  table_len = (u64)(-2) + 0x200            = 0x1FE        ← wraparound del SUMANDO
  table_len -= 0x1FE % 0x200 (=0x1FE)      = 0            ← asignación tamaño 0
  chequeo con signo: -0x200 < -1           = TRUE         ← pasa (ventana (-blsize, 0))
  sceFatfsCreateHeapVl(…, 0) → UVFAT_ReadDevice llena |data_len| sectores → OOB masivo
  ```
  El chequeo original ya existía en ≤13.50; v2 explota la ventana donde pasa
  (`-blsize < data_len < 0`) mientras la suma ya envolvió. El fix de 13.52 añade
  una comprobación de overflow previa al roundup, antes de la aritmética.
- **Estado en 13.52:** **PATCHED según el propio ASaudidos** — "the new firmware adds a
  pre-roundup overflow check before allocating the UpCase buffer". Verificación local
  imposible sin bytes del kernel 13.52 retail (artefacto AUSENTE en este lab);
  clasificada `PATCHED_PER_AUTHOR_REPORT/UNVERIFIED_LOCALLY`.
- **Techo de impacto incluso sin parche:** kernel panic (DoS). Ninguna demostración
  pública de corrupción controlada ⇒ no es vía de code execution ni de jailbreak.
- **Primitiva BD-J relacionada (separada):** `System.getSecurityManager()==null` +
  `sun.misc.Unsafe` = R/W arbitrario dentro del proceso BD-J (userland), sin acceso
  kernel.

## CVE-2026-7270 — execve() Buffer Overflow ❌ DISCARDED

- **Type:** Local privilege escalation
- **Component:** exec_args_adjust_args() in sys/kern/kern_exec.c
- **Bug:** Operator precedence error in memmove size calculation
- **Status:** DISCARDED — function introduced in FreeBSD 13.0, not present in FreeBSD 9, 10, 11, or 12. PS4 uses FreeBSD 9.
- **Verified:** Searched FreeBSD 9.0, 10.0, and 11.0 source trees
- **Conclusion:** Function was introduced in FreeBSD 12+, not present in PS4 kernel

## CVE-2026-49415 — execve() TOCTOU Race ⚠️ CANDIDATE

- **Type:** Local privilege escalation
- **Component:** execve(2) SUID handling in sys/kern/kern_exec.c
- **Bug:** TOCTOU race condition between credential check and application
- **Discovered by:** Synacktiv
- **Patched:** June 30, 2026 (after PS4 13.04 release)
- **Status:** CANDIDATE — SUID code confirmed present in FreeBSD 9
- **Evidence:** setsugid(), setugidsafety() found at lines 654-702 of kern_exec.c
- **Key code path:**
  1. VOP_GETATTR reads file attributes (SUID bit)
  2. credential_changing checks S_ISUID/S_ISGID
  3. setsugid() marks process
  4. PROC_UNLOCK → VOP_UNLOCK → window of vulnerability
  5. setugidsafety() closes insecure fds
- **Challenge:** PS4 may not have accessible SUID binaries from BD-J sandbox

## Celsius / ffs_mount — Integer Overflow 🔥 CONFIRMED

- **Type:** Kernel heap overflow
- **Component:** ffs_mountfs() in sys/ufs/ffs/ffs_vfsops.c
- **Discovered by:** bollars (via kernel diffing)
- **Works on:** PS4 up to 13.04, PS5 up to 12.70
- **Patched in:** PS4 13.50, PS5 13.00
- **Status:** CONFIRMED — vulnerable code present in FreeBSD 9

### Vulnerable code:
```c
// Line ~910 in ffs_vfsops.c
size = fs->fs_cssize;                          // from superblock (attacker controlled)
blks = howmany(size, fs->fs_fsize);
if (fs->fs_contigsumsize > 0)
    size += fs->fs_ncg * sizeof(int32_t);      // INTEGER OVERFLOW HERE
size += fs->fs_ncg * sizeof(u_int8_t);
space = malloc((u_long)size, M_UFSMNT, M_WAITOK);  // allocates SMALL buffer

// Later in the same function:
if (fs->fs_contigsumsize > 0) {
    fs->fs_maxcluster = lp = space;
    for (i = 0; i < fs->fs_ncg; i++)           // iterates fs_ncg times
        *lp++ = fs->fs_contigsumsize;           // HEAP OVERFLOW
    space = lp;
}
```

### Exploitation:
1. Craft UFS image with malicious superblock (fs_ncg = 0x40000001)
2. Mount via BD-J or Vue entry point
3. Integer overflow causes small malloc + massive heap write
4. Heap grooming needed to control what gets overwritten
5. Convert heap overflow to kernel read/write
6. Patch kernel, load payload

### Requirements:
- BD-J or Vue userland entry point
- 250GB+ HDD with malformed UFS image (per Victor's guidance)
- Kernel offsets for target firmware

### Superblock structure (key fields):
```
Offset in struct fs:
  fs_ncg           (u_int32_t) — controls the overflow
  fs_bsize         (int32_t)   — must pass validation checks
  fs_fsize         (int32_t)   — must pass validation checks
  fs_cssize        (int32_t)   — initial size value
  fs_contigsumsize (int32_t)   — must be > 0 to trigger vulnerable path
```

## MP4 Parser Vulnerability ⚠️ UNDER INVESTIGATION

- **Type:** Heap buffer overflow in multimedia parser
- **Component:** MP4/M4A atom parser (likely libSceAvPlayer)
- **Discovered by:** Shunsui
- **Confirmed on:** FW 11.00 (Media Player + SHAREfactory)
- **Likely affected:** All PS4 firmwares including 13.04 and 13.52

### Bug details:
- moov.udta.meta atom declares 90 bytes
- Child atom at offset 0x833 declares 190 bytes → exceeds parent
- Parser reads beyond buffer bounds → heap corruption
- Second corrupt atom at offset 0x885
- Media Player freezes, SHAREfactory gives error 34878-0

### Potential exploitation:
- Control overflow size by modifying declared atom size
- Control overflow content (attacker data in atom body)
- Possible to overwrite return addresses, vtable pointers, or heap metadata
- Needs core dump analysis to determine exact crash point and exploitability
