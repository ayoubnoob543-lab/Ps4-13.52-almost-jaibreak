# Proyecto autónomo de investigación — PS4 FW 13.52

Pipeline: exp00_gate → exp10_leak_tests → exp20_reclaim_tests → exp21_semctl_tests
→ analizador → siguiente hipótesis. Ejecutar con `./run.sh`.

## Hipótesis activas
| # | Hipótesis | Estado |
|---|---|---|
| H1 | UAF kqueue/knote reproducible en 13.52 | CONFIRMADO (hardware, investigador) |
| H2 | Reclaim por spray EVFILT_USER estable | CONFIRMADO (reinicialización limpia) |
| H3 | semctl (CVE-2026-58087) utilizable en 13.52 | **REFUTADA a nivel libkernel**: sin wrappers SysV en ninguna variante (ver results/stub_matrix.raw.json). Ruta residual: syscall directo desde exec nativa JIT + sysvsem presente en kernel (no verificable sin bytes retail) |
| H4 | Leak vía disclosure residual M_TEMP | Requiere consola (exp21) — solo viable si H3 resucita vía JIT |
| H5 | Corrupción controlable vía GETALL OOB write | Requiere consola; destructivo |

## Evidencia
- Integridad blob dual-anclado: PASS (results/exp01b_integrity.result.json)
- 212 stub sites / 210 syscalls distintas enumeradas en libkernel_sys 13.52
- Matriz de wrappers 5 módulos × 7 syscalls críticas: results/stub_matrix.raw.json

## Firmware / syscalls utilizadas
- Objetivo: PS4 FW 13.52 (Orbis, FreeBSD 9 base)
- En consola: kqueue(362), kevent(363), pipe(42), close(6), __semctl(220),
  semget(221), semop(222) — estas últimas AUSENTES en libkernel juego/sys

## Resultados locales (2026-08-24)
- exp01b_integrity: **PASS**
- exp01a_static_stubs: **PASS** (sanity mmap/read OK)
- exp00_gate: kqueue_uaf_path=**PASS**; semctl_via_libkernel=**FAIL**

## Siguiente hipótesis
H3-ref: ¿el kernel Orbis 13.52 aún implementa sysvsem a nivel kernel aunque el
wrapper userland no exista? Solo determinable mediante syscall directo 220 desde
ejecución nativa JIT (cadena mast1c0re/Luac0re) — experimento REQUIRES_HARDWARE.

## Reglas del proyecto
1-10 según encargo: PoC no destructivos, clasificación PASS/FAIL/UNKNOWN,
nunca afirmar KASLR leak sin puntero inequívoco, nunca convertir resultados en
R/W arbitrario ni ejecución kernel, documentar todo.
