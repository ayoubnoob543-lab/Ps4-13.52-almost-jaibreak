# Investigación OFFLINE 13.52 — síntesis sin hardware (2026-08-24)

Todo lo determinable sin consola, con separación estricta de niveles de confirmación.
Fuentes archivadas: `analysis/sources/freebsd-9.1/`, `results/stub_matrix.raw.json`,
`results/stub_sets_full.json`, `analysis/kqueue_uaf_1352_observations_v2_*.json`.

## A. Comparativa libkernel 9.00–12.52 (+ libkernel_sys 13.52)

| Módulo | stubs totales | kqueue(362) | kevent(363) | SysV sem/msg/shm |
|---|---|---|---|---|
| lk_9_00.elf | 387 | ✓ | ✓ | ✗ |
| lk_11_02.elf | 389 | ✓ | ✓ | ✗ |
| lk_12_00.elf | 389 | ✓ | ✓ | ✗ |
| lk_12_52.elf | 389 | ✓ | ✓ | ✗ |
| libkernel_sys_13.52 (raw) | 210 distintos | ✗ | ✗ | ✗ |

Conclusiones extrapolables legítimamente:
1. El set de wrappers del libkernel de juego está **congelado desde 11.02**
   (idéntico 389 en tres versiones mayores) ⇒ extrapolar su estructura a 13.xx es
   razonable como hipótesis fuerte, no certeza.
2. **SysV IPC jamás tuvo wrapper en el libkernel de juego** en ninguna versión ⇒
   la vía semctl está muerta para procesos normales en TODA la línea, no es un
   recorte de 13.52.
3. Existen al menos DOS variantes de libkernel en 13.52 (sys vs juego); el dump
   dual-anclado local es la variante sys reducida. No confundir inventarios.
4. 11.02 eliminó las syscalls 678/679 respecto a 9.00 (único churn observado).

NO extrapolable sin bytes retail: tabla de syscalls del KERNEL, prison gates,
sanitizaciones añadidas por Sony, presencia real de sysvsem en kernel.

## B. Ciclo de vida knote/kqueue en FreeBSD 9.1 (fuente archivada)

Hechos verificados en `kern_event_f91.c`:
- `knote_zone` UMA dedicada (L183); alloc/free vía uma (no malloc buckets).
- Sincronización SOLO por flag `KN_INFLUX` bajo lock del kq. Sin comentario
  engañoso: hay un `/* XXX - ensure not KN_INFLUX?? */` (L189) reconociendo
  dudas del propio upstream.
- **Cero `kn_usecount`** — el refcounting que cierra estas carreras llegó a
  FreeBSD mucho después ⇒ Orbis-F9 no lo tiene ⇒ consistente con el UAF
  reproducido en hardware.
- 🆕 **`kqueue_scan()` aloca un MARKER desde knote_zone en CADA kevent()**
  (`marker = knote_alloc(1)`), y solo fija `kn_status=KN_MARKER`: el resto del
  slot conserva contenido previo. Esto abre una técnica NUEVA para la brecha 2:
  reclaim por MARKERS (kevents bloqueados/concurrentes) en lugar de knotes
  EVFILT_USER — sin reinicialización de `kn_fop`/`kn_hook`, habilitando los
  experimentos de ghost-read y doble-procesamiento que el spray tipado impedía.

## C. Barrido público específico 13.52

| Hallazgo | Fuente | Nivel |
|---|---|---|
| 13.52 parcheó el exploit Blu-ray vigente ≤13.50 | MODDED WARFARE 2026-06-17; psdevwiki (hash sunjce cambiado, zecoxao) | CONFIRMADO_PÚBLICO |
| Bug userland BD-J "fully achieved" en 13.52 (TheeEvolutionYT) | YouTube 2026 | CLAIM_COMUNITARIO_SIN_POCPUB |
| UltraC0re: userland via Jak-X Combat Racing para FW recientes | MODDED WARFARE 2026-06-17 | PUBLICADO, rango FW exacto por verificar |
| Luac0re JIT nativo: PS4 hasta 13.02 (v1.1, mar-2026); README v2.x dice "latest firmwares"; Suchi96 afirma 13.52 retail | nydus 2026-03-10; repo; docx | AUTOR_REPORTADO (dos fuentes independientes) |
| elf-arsenal actualizado para FW nuevos | MODDED WARFARE | referencial |

## D. TABLA MAESTRA DE HIPÓTESIS

| HIPÓTESIS | EVIDENCIA | FUENTE | CONFIRMACIÓN | BLOQUEO |
|---|---|---|---|---|
| UAF knote existe y es reproducible en 13.52 | crash sin spray, estabiliza con spray | notas investigador (HW) | **CONFIRMADO_PS4_13.52** (autor-reportado) | — |
| Reclaim intra-zona posible | spray 50–200 knotes OK | HW investigador | CONFIRMADO_PS4_13.52 | reinicialización limpia limita control |
| Marker-reclaim sin reinicialización (nueva técnica) | código F9.1 L~scan | fuentes FreeBSD | CONFIRMADO_FREEBSD (mecánica) | REQUIRES_HARDWARE para observar en Orbis |
| Sin refcount knote en base Orbis | ausencia kn_usecount en F9.1 | fuente FreeBSD | CONFIRMADO_FREEBSD | diff kernel retail pendiente |
| Corrupción controlable (GETALL OOB write u16≤0x7FFF) | código verbatim sysv_sem L737 | fuente FreeBSD | CONFIRMADO_FREEBSD / HIPÓTESIS_EN_ORBIS | sin wrappers userland ⇒ requiere exec nativa JIT |
| Info leak vía disclosure residual M_TEMP | mecanismo copyout count-viejo | fuente FreeBSD | HIPÓTESIS | REQUIRES_HARDWARE (+resucitar semctl vía JIT) |
| KASLR leak | 760 KB examinados = 0 punteros; sanitización activa | HW investigador | NO_LOGRADO_13.52 | candidatos: churn+sysctls, markers, rtsock — todos REQUIRES_HARDWARE |
| Kernel R/W estable | nada público ni privado | — | NO_ALCANZADO | depende de leak+control |
| Ejecución kernel | nada público | — | NO_ALCANZADO | ídem |
| Vía userland 13.52 disponible | BD-J claim comunitario + JIT autor-reportado ×2 + UltraC0re | escena | PARCIAL (claims) | PoC público completo pendiente |
| semctl utilizable por proceso normal | wrappers ausentes SIEMPRE | dumps 5 módulos | REFUTADO_OFFLINE | solo ruta residual: syscall directo vía JIT |
| exFAThax v2 utilizable | ASaudidos: fix añadido en FW nuevo | X/twitter | REFUTADO_13.52 (reporte autor) | verificar in-situ imposible sin kernel bytes |

## E. Nuevos experimentos offline creados
- `experiments/exp01a_static_stubs` (enumeración stubs, sanity mmap/read)
- `research/run.sh` pipeline completo con parada automática en hardware (regla 10)

## F. Incógnitas marcadas explícitamente
- [REQUIRES_HARDWARE] ¿marker-reclaim evita reinicialización en Orbis real?
- [REQUIRES_HARDWARE] ¿sysvsem vive en kernel 13.52?
- [REQUIRES_HARDWARE] ¿rtsock accesible desde sandbox 13.52?
- [IMPOSIBLE_SIN_BYTES_RETAIL] offsets absolutos del kernel, KASLR base,
  verificación de parches Sony 13.52.


## ADENDA FINAL (2026-08-24 tarde): formato interno PUP documentado + composición identificada
- Formato completo público en psdevwiki/PUP: metadata entries 0x50B con AES128 key+IV+HMAC por segmento, cifrados bajo clave estática por-FW en la cabecera.
- Nuestro PUP 13.52 contiene (por IDs psdevwiki + mapa C++): secure_modules(5), SYSTEM fs(6) — kernel retail dentro— , EAP(7/8), PREINST(9), SYSTEM_EX(12), orbis_swu.self(512/514), SECURE LOADER per-console, SYSCON…
- Entropía 100% medida en ambos PUPs internos ⇒ sin huecos en claro.
- Detalles: research/results/offline_scan.json · analysis/sources/psdevwiki/PUP_format_snapshot.md
