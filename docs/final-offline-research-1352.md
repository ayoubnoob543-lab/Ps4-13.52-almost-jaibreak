# INVESTIGACIÓN OFFLINE FINAL — PS4 FW 13.52 (cierre 2026-08-24)

Consolidación exhaustiva de todo lo determinable sin consola. Fuentes primarias:
código FreeBSD 9.1 archivado (`analysis/sources/freebsd-9.1/`, hashes en
`SHA256SUMS`), dumps libkernel 9.00–12.52 (`research/libkernel/`),
`results/stub_matrix.raw.json`, observaciones HW del investigador
(`analysis/kqueue_uaf_1352_observations_v2_*.json`), advisories FreeBSD
SA-26:54 / SA-26:50, writeup Cryptogenic 5.05 (exploit-db 45045).

---

## 1. ESTADO ACTUAL COMPLETO

```text
[✓] UAF kqueue/knote        CONFIRMADO_PS4_13.52 (HW, autor-reportado)
[✓] reclaim                 CONFIRMADO_PS4_13.52 (spray EVFILT_USER estable)
[✗] MARKER leak             REFUTADO_OFFLINE (M_ZERO incondicional, L2167–69)
[?] double-free             MECÁNICA CONFIRMADA_FREEBSD · ventana REQUIRES_HARDWARE
[?] heap disclosure         MECÁNICA CONFIRMADA_FREEBSD · bloqueada por wrapper-absent ⇒ REQUIRES_HARDWARE+JIT
[✗] KASLR leak              NO_LOGRADO (0 punteros en ~760 KB) — sin vía offline restante
[✗] kernel R/W              NO_ALCANZADO (depende leak+corrupción)
[✗] ejecución               NO_ALCANZADO
```

## 2–3. HIPÓTESIS CON EVIDENCIA Y FUENTE

### PRIORIDAD 1 — DOUBLE-FREE

Ciclo de vida verificado (sysv/kern_event.c F9.1):
- Alloc: `uma_zalloc(knote_zone, |M_ZERO)` — celda SIEMPRE a cero.
- Uso: flags KN_* bajo lock del kq; `KN_INFLUX` marca procesamiento.
- Liberación única legítima: `knote_drop()` → unlink de listas → `fdrop(file)` →
  `kn_fop=NULL` → `knote_free()` = `uma_zfree(knote_zone)`.
- Consumidor concurrente: `kqueue_scan()` recorre TAILQ con marker centinela;
  ONESHOT: `*kevp=kn->kn_kevent; f_detach; knote_drop` fuera de lock.

**Mecánica double-free determinada (mixto código/hipótesis):**
1. [CONFIRMADO_CÓDIGO] Segunda pasada de `knote_drop` sobre celda con
   `fop==NULL` crashea (null-deref en `f_isfd`) ⇒ no hay double-free "gratis".
2. [CONFIRMADO_CÓDIGO] Si la celda fue reclamada por un knote REAL K2
   (`fop=user_filterops` válido), la segunda pasada completa el drop y ejecuta
   `knote_free(K2_cell)` con K2 vivo ⇒ **double-free real + fdrop extra del file**
   (segundo vector: refcount de pipe corrompido).
3. [CONFIRMADO_HW] El stale-reference existe y es alcanzable (UAF reproducido).
4. [HIPÓTESIS — REQUIRES_HARDWARE] Que la entrada stale persista en listas de
   kq_A tras el primer drop (la ventana exacta depende del binario Orbis; en
   F9.1 el unlink ocurre dentro de knote_drop bajo INFLUX).
5. [REFUTADO_OFFLINE] Receta dup()/close ingenua: `close(fd1)` con fd2 vivo NO
   desmonta el knote (fdrop solo al último ref) ⇒ no produce segunda liberación
   por sí sola.
- Precedentes históricos válidos como plantilla: Cryptogenic 5.05 BPF
  (double-free→poisoning→fake knote→f_detach→JOP) — NO asumir portable a
  13.52 (SMAP/SMEP activos; fake-knote-en-userland inviable hoy).
- Estructuras intervinientes: knote_zone (UMA), kq_knlist/kq_knhash (SLIST),
  kq_head (TAILQ queued), struct file refcount, sema/M_TEMP (vía semctl si
  existiera).

### PRIORIDAD 2 — DISCLOSURE / HEAP (inventario completo)

| Ruta | Código fuente | Allocator | Init/cero | ¿Punteros? | ¿Copyout? | Leak público | Veredicto |
|---|---|---|---|---|---|---|---|
| kern.37/47/48 | sysctl handlers (no localizados sin kernel) | ? | ? | empíricamente 0 | sí | ninguno | REQUIRES_HARDWARE (churn-retest) |
| GETALL residual | sysv_sem.c L737–767 ✓archivado | malloc M_TEMP count*2 | SIN zero (malloc) | residuales posibles | sí (count viejo) | ninguno específico | MECÁNICA OK; bloqueada por wrappers ausentes |
| SETALL oráculo | sysv_sem.c L805+ ✓ | ídem | sin zero | lee adyacente→sems→GETVAL | indirecto | ninguno | ídem |
| MARKER | kern_event.c L1345/2167 | uma knote_zone | M_ZERO total | no | nunca (skip) | n/a | REFUTADO |
| kevent copyout normal | L1420 *kevp=kn_kevent | — | user-set | no (solo campos user) | sí | n/a | sin valor leak |
| kinfo_proc | kernel Sony | ? | ? | SANITIZADO (HW) | sí | — | descartado empíricamente |
| /dev/gc, /dev/random, socket opts | — | — | — | 0 empírico | — | — | descartado |

Conclusión P2: la ÚNICA mecánica de disclosure con base en código es la familia
semctl (GETALL residual + SETALL oracle), y está bloqueada aguas arriba por la
ausencia de wrappers (ver P3). Sin ella, no queda ninguna ruta de leak
identificada en código accesible.

### PRIORIDAD 3 — SEMCTL

- Syscalls amd64 F9: `__semctl=220, semget=221, semop=222` (msgget 225,
  shmget 231). Wrappers en libkernel de juego: **AUSENTES en 9.00–12.52**
  (matriz 5×7, results/stub_matrix.raw.json) ⇒ procesos normales jamás pudieron
  llamarlas vía libkernel.
- Kernel implementa sysvsem: **UNKNOWN — REQUIRES_KERNEL_BYTES/HARDWARE**.
  La opción SYSVSEM es GENÉRIC-en F9, pero Sony pudo compilarla fuera; el gate
  `prison_allow(PR_ALLOW_SYSVIPC)` añade segundo filtro desconocido.
- Separación estricta: **libkernel expone: NO (probado) · kernel implementa:
  DESCONOCIDO · utilizable hoy: NO**.
- Ruta residual teórica: syscall 220 directa desde exec nativa JIT
  (mast1c0re/Luac0re, autor-reportado en FW recientes) + kernel con sysvsem +
  prison gate abierto. Triple condición sin evidencia pública.

### PRIORIDAD 4 — CVE-2026-58083 (kqueue copy-on-fork)

- Advisory SA-26:50.kqueue: afecta **FreeBSD 15.1 únicamente** (stable/15,
  releng/15.1-p2). Bug en modo `KQUEUE_CPONFORK` (duplicación de knotes en
  fork()) + timer filter disparando durante la copia.
- Determinación: la característica CPONFORK **no existe en FreeBSD 9** ⇒ el
  código vulnerable no puede estar presente en la base Orbis.
- **Clasificación: REFUTADO_ORBIS / NO_APLICA** (CONFIRMADO_OTRO_FIRMWARE como
  bug real de FreeBSD moderno). Sin evidencia PS4 aplicable.

### PRIORIDAD 5 — Barrido global

Sin nuevo material técnico beyond lo ya integrado. Rumores/vídeos descartados
por falta de evidencia técnica (BD-J userland 13.52 "achieved": claim sin PoC
público; se mantiene como PARCIAL en docs previos). Referencias técnicas
consolidadas: Cryptogenic 5.05 writeup, venglin kqueue F6.1, advisories
SA-26:54/26:50, psdevwiki Bugs/Vulnerabilities, repos Suchi96/Gezine/McCaulay.

---

## 4. QUEDÓ CONFIRMADO
- UAF + reclaim en 13.52 (HW). Layout knote 0x80 triple-fuente.
- Mecánicas GETALL-write / SETALL-read / disclosure-residual (código F9.1).
- Ausencia estructural de SysV wrappers en libkernel (todas versiones).
- M_ZERO elimina residuos vía markers. CVE-2026-58083 no aplica a base F9.

## 5. QUEDÓ REFUTADO
- MARKER como leak/observador. dup/close naive para doble liberación.
- semctl utilizable por proceso normal. exFAThax v2 en 13.52 (reporte autor).
- BD-J sunjce en 13.52. CVE-2026-58083 aplicable a Orbis.

## 6. DESCONOCIDO (sin poder resolver offline)
- Presencia de sysvsem en kernel 13.52. Prison gates reales. Vecinos de heap
  del knote_zone en Orbis. Sanitizaciones adicionales Sony. Estado exacto de
  todos los offsets kernel.

## 7. SOLO DETERMINABLE CON HARDWARE
- Ejecución de exp00_gate.lua (mapa sandbox vivo), exp10, par exp20/21.
- Validación de marker-reclaim estabilizador. Ventanas de carrera reales.
- Cualquier medición de punteros kernel reales.

## 8–9. EXPERIMENTOS EN COLA (con criterio de validación/refutación)

| Exp | Qué valida | PASS si | REFUTADO si |
|---|---|---|---|
| exp00_gate.lua | wrappers vivos en consola | stubs presentes + semget OK | wrapper ausente o ENOSYS |
| exp10_leak_churn.lua | sanitización post-churn | aparece candidato rango-kernel estable | 0 candidatos en 30 rondas |
| exp20/21 par | disclosure residual GETALL | bytes ≠0 estables en cola con forma puntero | colas siempre 0 tras ≥5000 intentos |
| SETALL-oracle (nuevo, requiere par) | mapa heap adyacente | ERANGE/valores posicionales reproducibles | todo-ceros estable |
| Exp 2 GETALL-write | corrupción dirigida | crash forense identifica objeto vecino | sin efecto tras barrido |
| marker-stabilizer | walk estable post-UAF sin spray | escenario sobrevive N iteraciones | crash consistente |

---

## CHECKLIST MANTENIDA

```text
[✓] UAF                    CONFIRMADO_PS4_13.52
[✓] reclaim                CONFIRMADO_PS4_13.52
[✗] MARKER leak            REFUTADO_OFFLINE (M_ZERO)
[?] double-free            MECÁNICA_OK / VENTANA REQUIRES_HARDWARE
[?] heap disclosure        MECÁNICA_OK / REQUIRES_HARDWARE (+JIT por wrappers ausentes)
[✗] KASLR leak             NO_LOGRADO · sin ruta offline restante
[✗] kernel R/W             NO_ALCANZADO
[✗] ejecución              NO_ALCANZADO
```

Regla vigente: nada de esto se convierte en R/W/ejecución sin evidencia medida
en hardware. Todo hallazgo futuro entra por el pipeline research/run.sh con su
result.json y clasificación.

---

## RONDAS ADICIONALES (2026-08-24 tarde) — verificación numérica y nuevas primitivas

### R1 — Numerología verificada contra sys/syscall.h F9.1 (archivado)
- CONFIRMADO: kqueue=362, kevent=363, semget=221, semop=222, msgget=225,
  shmget=231, pipe=42, close=6 — tabla base IDÉNTICA a la reportada en PS4.
- **CORRECCIÓN**: `SYS___semctl` = **510** en F9.1 (no 220 como se asumió antes).
  Re-barrido completo con números correctos (220 compat, 510 actual, 224 msgctl,
  229 shmctl, rangos IPC 216–232 y 505–515): **siguen AUSENTES en los 5 módulos**
  ⇒ la refutación de wrappers sobrevive con numerología correcta.
- Único falso positivo: 232 = clock_gettime (mundano).
- **EVFILT diff confirmado**: stock F9.1 TIMER=-7 / FS=-9 / LIO=-10 / USER=-11;
  PS4 reporta USER=-7 / FS=-8 ⇒ Sony ELIMINÓ TIMER y renumeró. Implicancia:
  sin timer-knotes en PS4 ⇒ patrones tipo CVE-2026-58083 (timer durante copia)
  estructuralmente imposibles; spray por timers indisponible.

### R1c — Layout compilable verificado (exp01c_layout_verify/)
Struct transcrito del header archivado + clang x86_64:
13/13 offsets byte-exactos vs medición HW (sizeof=0x80, kevent@0x30 32B,
fop@0x68...). Artefacto reproducible sin PS4.

### R2 — Primitiva de escritura controlada post-reclaim (CONFIRMADO_CÓDIGO)
`filt_usertouch` (kern_event.c): cada re-registro EVFILT_USER escribe sobre el
slot reclamado `kn_sfflags@0x54` (u32 arbitrario vía NOTE_FFCOPY) y
`kn_sdata@0x58` (i64 completo). Primer write controlado post-reclaim; NO alcanza
kn_fop@0x68. Además `filt_user` devuelve hookid ⇒ trigger determinista vía
NOTE_TRIGGER. `filt_userattach` confirma observación HW: `kn_hook=NULL`.

### R3 — Camino kqueue_close + doble-drop
`kqueue_close`: espera TASKDRAIN → deslinkea de fdp → destruye knlist → libera.
Los knotes restantes se dropean en el drain ⇒ si una entrada stale persiste en
esas listas tras el primer free, cerrar kq_A ejecuta `knote_drop` sobre la celda
viva de K2 ⇒ **double-free real + fdrop extra del file** (segundo vector de
corrupción por refcount de pipe). Persistencia del stale-entry = REQUIRES_HARDWARE.
Cita upstream del refcount: no localizada con precisión; la AUSENCIA en 9.1 está
probada por inspección directa (más fuerte que cualquier cita).

### Toolkit ampliado
- `exp22a_oracle_attacker.lua` + `exp22b_oracle_victim.lua` (oráculo SETALL,
  roadmap §1b): par listo para consola con detección automática de residuos.

## CHECKLIST FINAL

```text
[✓] UAF                    CONFIRMADO_PS4_13.52
[✓] reclaim                CONFIRMADO_PS4_13.52
[✗] MARKER leak            REFUTADO_OFFLINE (M_ZERO)
[?] double-free            MECÁNICA OK · ventana REQUIRES_HARDWARE
[?] heap disclosure        MECÁNICA OK · bloqueada por wrappers (REQUIRES_HARDWARE+JIT)
[?] write intra-slot       NUEVO: CONFIRMADO_CÓDIGO (filt_usertouch 0x54/0x58)
[✗] KASLR leak             NO_LOGRADO · sin ruta offline restante
[✗] kernel R/W             NO_ALCANZADO
[✗] ejecución              NO_ALCANZADO
```
