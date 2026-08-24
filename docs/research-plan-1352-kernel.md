# Plan de investigación kernel PS4 13.52 — kqueue UAF + semctl TOCTOU

Versión revisada tras análisis estático de las fuentes FreeBSD 9.1 archivadas en
`analysis/sources/freebsd-9.1/` (SHA-256 en `SHA256SUMS`). Sustituye al borrador
previo; corrige la dirección de las primitivas GETALL/SETALL.

## Mapa de primitivas REAL según código fuente (sysv_sem.c L737–845)

| Escenario carrera | Qué pasa | Primitiva | Riesgo |
|---|---|---|---|
| Snapshot GRANDE → set nuevo PEQUEÑO (GETALL) | loop llena poco; `copyout` copia count VIEJO | **Disclosure residual** del heap M_TEMP (cola del array sin sobrescribir) | Seguro: iterables sin panic |
| Snapshot PEQUEÑO → set nuevo GRANDE (**GETALL**) | `array[i]=semval` hasta nsems NUEVO | **OOB WRITE** a heap adyacente con u16 controlados | Alto: panic probable |
| Snapshot PEQUEÑO → set nuevo GRANDE (**SETALL**) | lee `array[i]` OOB y guarda en `sem_base[i]` | **OOB READ→userland** vía GETVAL posterior (oráculo limpio) | Medio: ERANGE corta antes si hay valor >0x7FFF |

Restricciones duras:
- Contenido de semvals limitado por `semvmx` (típico **0x7FFF**): no existen patrones
  0xFFFF; marcadores tipo 0x4141 sí son válidos.
- La validación de secuencia envuelve cada **0x8000** recreaciones del mismo índice.
- **Fallo silencioso**: una carrera perdida devuelve EINVAL limpio (el copyin/copyin
  previo es inocuo) ⇒ reintentar es gratis; el éxito se detecta por efectos, no por errores.

## Experimentos (ordenado por información ganada)

### Exp 0 — Gate de sandbox (bloqueante)
Sondear `semget/semctl/semop` bajo UID=1 con handler de SIGSYS + errno map.
Gate: `prison_allow(cred, PR_ALLOW_SYSVIPC)` (sysv_sem.c L593/L868).
Si ENOSYS sistemático ⇒ vía muerta; documentar y pasar al plan B (UAF timing).

### Exp 1a — Disclosure por copyout residual (GETALL grande→pequeño)
Churn previo de M_TEMP con objetos ricos en punteros; carrera para reemplazo por set
pequeño; `copyout` largo devuelve cola residual. Métrica: bytes ≠ 0 estables entre
ejecuciones y valores con forma de puntero (0x800000000–0xFFFF... rango típico kernel).
**No corrompe nada: iteración ilimitada.**

### Exp 1b — Oráculo OOB-read por SETALL (pequeño→grande)
Tras la carrera, `GETVAL(i)` para i ≥ count viejo vuelca bytes adyacentes.
Ventaja frente a 1a: lectura byte-a-byte dirigida con aborto ERANGE informativo
(la posición del primer >0x7FFF ya es información del contenido).

### Exp 2 — OOB WRITE por GETALL (pequeño→grande) — destructivo
Patrón marcador válido (p. ej. 0x4141) en semvals del set nuevo; forense del panic =
identidad del objeto vecino corrupto. Repetir variando `count` para barrer offsets del
slab. **Cada intento puede costar un reboot.**

### Exp 3 — Composición
Si 1a/1b dan KASLR y 2 da corrupción dirigida de un objeto con puntero de función en
M_TEMP (candidatos: sbuf, mount args, temp structs de path resolution), cerrar R/W.
El UAF de knotes queda como plan B y oráculo de timing.

## Registro obligatorio por experimento
errno exactos, tamaños usados, nº de intentos hasta hit, bytes residuales crudos,
patrón escrito y trace de panic capturada. Sin estos, el resultado no entra en el lab.

## Estado heredado (verificado)
- UAF kqueue/knote: reproducible en HW 13.52; spray EVFILT_USER reclama slot con
  reinicialización limpia (`kn_fop=&user_filterops`); 0 leaks en ~760 KB examinados.
- exFAThax v2 / BD-J sunjce: parcheados en 13.52.
- CVE-2026-58087: patrón verbatim presente en base F9.1; wiki: "Patched: No as of
  PS4 13.52"; sin PoC público en consola.
